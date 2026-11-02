from pathlib import Path
from collections import defaultdict
import hashlib
import csv
import yaml

from PIL import Image, UnidentifiedImageError

# ACS - Configuration

ROOT = Path(__file__).resolve().parents[2]

CONFIG_PATH = ROOT / "configs/classes.yaml"

DATASET_PATH = ROOT / "datasets/classification/raw"

METADATA_PATH = ROOT / "datasets/metadata"

RESULTS_PATH = ROOT / "results/tables"

SESSIONS = ["S01", "S02", "S03"]

FORMATS = {
    ".jpg", ".jpeg", ".png"
}


# Chargement des classes
def load_config():

    with open(CONFIG_PATH, "r", encoding="utf-8") as file:
        config = yaml.safe_load(file)

    return config


# Calcul du hash SHA256
def calculate_hash(image_path):

    sha256 = hashlib.sha256()

    with open(image_path, "rb") as file:

        for block in iter(lambda: file.read(1024 * 1024), b""):
            sha256.update(block)

    return sha256.hexdigest()


# Vérification des images
def verify_image(image_path):

    try:

        with Image.open(image_path) as image:
            image.verify()

        with Image.open(image_path) as image:

            width, height = image.size
            mode = image.mode

        return width, height, mode

    except (OSError, ValueError, UnidentifiedImageError):

        return None

# Analyse du dataset
def analyze_dataset(config):

    records = []
    issues = []

    hashes = {}

    statistics = defaultdict(int)

    variantes = config["variantes"]

    for image_path in sorted(DATASET_PATH.rglob("*")):

        if not image_path.is_file():
            continue

        if image_path.suffix.lower() not in FORMATS:

            if image_path.suffix.lower() in {".heic", ".heif"}:
                issues.append({
                    "image_path": str(image_path),
                    "probleme": "Format HEIC non pris en charge"
                })

            continue

        relative_path = image_path.relative_to(DATASET_PATH)

        parts = relative_path.parts

        # Structure attendue :
        # type/couleur/session/image.jpg

        if len(parts) != 4:

            issues.append({
                "image_path": str(image_path),
                "probleme": "Structure du répertoire invalide"
            })

            continue

        bonbon_type, couleur, session, filename = parts

        # Vérification des étiquettes

        if bonbon_type not in variantes:

            issues.append({
                "image_path": str(image_path),
                "probleme": "Type inconnu"
            })

            continue

        if couleur not in variantes[bonbon_type]:

            issues.append({
                "image_path": str(image_path),
                "probleme": "Couleur invalide pour ce type"
            })

            continue

        if session not in SESSIONS:

            issues.append({
                "image_path": str(image_path),
                "probleme": "Session inconnue"
            })

            continue

        # Vérification du fichier

        image_info = verify_image(image_path)

        if image_info is None:

            issues.append({
                "image_path": str(image_path),
                "probleme": "Image corrompue ou illisible"
            })

            continue

        width, height, mode = image_info

        # Détection des doublons exacts

        image_hash = calculate_hash(image_path)

        if image_hash in hashes:

            issues.append({
                "image_path": str(image_path),
                "probleme": (
                    "Doublon exact de "
                    + str(hashes[image_hash])
                )
            })

        else:

            hashes[image_hash] = image_path

        # Identifiant stable basé sur le chemin

        image_id = hashlib.sha256(
            relative_path.as_posix().encode("utf-8")
        ).hexdigest()[:16]

        # Enregistrement des métadonnées

        records.append({

            "image_id": image_id,

            "image_path": image_path.relative_to(ROOT).as_posix(),

            "type": bonbon_type,

            "couleur": couleur,

            "session_id": session,

            "width": width,

            "height": height,

            "mode": mode,

            "sha256": image_hash

        })

        statistics[(bonbon_type, couleur, session)] += 1

    return records, issues, statistics

# Génération des fichiers CSV
def save_csv(records, issues, statistics, config):

    METADATA_PATH.mkdir(parents=True, exist_ok=True)

    RESULTS_PATH.mkdir(parents=True, exist_ok=True)

    # Fichier principal

    output_path = METADATA_PATH / "classification.csv"

    fields = [
        "image_id",
        "image_path",
        "type",
        "couleur",
        "session_id",
        "width",
        "height",
        "mode",
        "sha256"
    ]

    with open(output_path, "w", newline="", encoding="utf-8") as file:

        writer = csv.DictWriter(file, fieldnames=fields)

        writer.writeheader()

        writer.writerows(records)

    # Rapport des problèmes

    issues_path = METADATA_PATH / "issues.csv"

    with open(issues_path, "w", newline="", encoding="utf-8") as file:

        writer = csv.DictWriter(
            file,
            fieldnames=["image_path", "probleme"]
        )

        writer.writeheader()

        writer.writerows(issues)

    # Statistiques par variante

    stats_path = RESULTS_PATH / "dataset_summary.csv"

    with open(stats_path, "w", newline="", encoding="utf-8") as file:

        writer = csv.writer(file)

        writer.writerow([
            "type", "couleur", "S01", "S02", "S03", "total"
        ])

        for bonbon_type, couleurs in config["variantes"].items():

            for couleur in couleurs:

                counts = [
                    statistics[(bonbon_type, couleur, session)]
                    for session in SESSIONS
                ]

                writer.writerow([
                    bonbon_type,
                    couleur,
                    *counts,
                    sum(counts)
                ])

    return output_path, issues_path, stats_path


def main():
    config = load_config()

    records, issues, statistics = analyze_dataset(config)

    output_path, issues_path, stats_path = save_csv(
        records, issues, statistics, config
    )

    print(f"\nImages valides : {len(records)}")

    print(f"Problèmes détectés : {len(issues)}")

    print(f"Nombre de types : {len(config['types'])}")

    n_variantes = sum(
        len(colors)
        for colors in config["variantes"].values()
    )

    print(f"Nombre de variantes : {n_variantes}")

    print("\nFichiers générés :")

    print(output_path.relative_to(ROOT))
    print(issues_path.relative_to(ROOT))
    print(stats_path.relative_to(ROOT))

    print("\nAnalyse terminée !")


if __name__ == "__main__":
    main()
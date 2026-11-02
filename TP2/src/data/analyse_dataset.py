from pathlib import Path
import math

import pandas as pd
import matplotlib.pyplot as plt
from PIL import Image, ImageOps
import yaml

# ACS - Configuration
ROOT = Path(__file__).resolve().parents[2]

CONFIG_PATH = ROOT / "configs/classes.yaml"

DATASET_CSV = ROOT / "datasets/metadata/classification.csv"

OUTPUT_DIR = ROOT / "results/figures"

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


# Chargement des données
def load_data():

    with open(CONFIG_PATH, "r", encoding="utf-8") as file:
        config = yaml.safe_load(file)

    df = pd.read_csv(DATASET_CSV)

    required_columns = [
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

    missing = [
        column for column in required_columns
        if column not in df.columns
    ]

    if missing:
        raise ValueError(
            f"Colonnes manquantes : {missing}"
        )

    return df, config

# Distribution des types
def plot_types(df, config):

    types = config["types"]

    counts = (
        df["type"]
        .value_counts()
        .reindex(types, fill_value=0)
    )

    fig, ax = plt.subplots(figsize=(10, 5))

    counts.plot.bar(ax=ax)

    ax.set_title("Distribution des types de bonbons")
    ax.set_xlabel("Type de bonbon")
    ax.set_ylabel("Nombre d'images")

    ax.tick_params(axis="x", rotation=30)

    fig.tight_layout()

    fig.savefig(
        OUTPUT_DIR / "distribution_types.png",
        dpi=300
    )

    plt.close(fig)

# Distribution des variantes
def plot_variantes(df, config):

    variantes = [
        (bonbon_type, couleur)
        for bonbon_type, couleurs in config["variantes"].items()
        for couleur in couleurs
    ]

    counts = df.groupby(["type", "couleur"]).size()

    counts = counts.reindex(
        pd.MultiIndex.from_tuples(
            variantes,
            names=["type", "couleur"]
        ),
        fill_value=0
    )

    labels = [
        f"{bonbon_type} - {couleur}"
        for bonbon_type, couleur in counts.index
    ]

    fig, ax = plt.subplots(figsize=(11, 9))

    ax.barh(labels, counts.values)

    ax.set_title("Distribution des variantes")
    ax.set_xlabel("Nombre d'images")

    ax.invert_yaxis()

    fig.tight_layout()

    fig.savefig(
        OUTPUT_DIR / "distribution_variantes.png",
        dpi=300
    )

    plt.close(fig)

# Distribution des sessions
def plot_sessions(df, config):

    sessions = ["S01", "S02", "S03"]

    counts = (
        df.groupby(["type", "session_id"])
        .size()
        .unstack(fill_value=0)
        .reindex(
            index=config["types"],
            columns=sessions,
            fill_value=0
        )
    )

    ax = counts.plot(
        kind="bar",
        stacked=True,
        figsize=(10, 6)
    )

    ax.set_title("Distribution des sessions d'acquisition")
    ax.set_xlabel("Type de bonbon")
    ax.set_ylabel("Nombre d'images")

    ax.tick_params(axis="x", rotation=30)

    plt.tight_layout()

    plt.savefig(
        OUTPUT_DIR / "distribution_sessions.png",
        dpi=300
    )

    plt.close()

# Résolution des images
def plot_resolution(df):

    width = pd.to_numeric(df["width"], errors="coerce")
    height = pd.to_numeric(df["height"], errors="coerce")

    valid = width.notna() & height.notna()

    fig, ax = plt.subplots(figsize=(9, 6))

    ax.scatter(
        width[valid],
        height[valid],
        alpha=0.5
    )

    ax.set_title("Résolution des images")
    ax.set_xlabel("Largeur (pixels)")
    ax.set_ylabel("Hauteur (pixels)")

    fig.tight_layout()

    fig.savefig(
        OUTPUT_DIR / "resolution_images.png",
        dpi=300
    )

    plt.close(fig)

# Visualisation des échantillons
def plot_samples(df, config):

    variantes = [
        (bonbon_type, couleur)
        for bonbon_type, couleurs in config["variantes"].items()
        for couleur in couleurs
    ]

    cols = 4
    rows = math.ceil(len(variantes) / cols)

    fig, axes = plt.subplots(
        rows,
        cols,
        figsize=(14, rows * 3.5)
    )

    axes = axes.flatten()

    for ax, (bonbon_type, couleur) in zip(
        axes, variantes
    ):

        subset = df[
            (df["type"] == bonbon_type) &
            (df["couleur"] == couleur)
        ]

        ax.axis("off")

        ax.set_title(
            f"{bonbon_type} - {couleur}",
            fontsize=10
        )

        if subset.empty:
            ax.text(
                0.5, 0.5,
                "Aucune image",
                ha="center",
                va="center",
                transform=ax.transAxes
            )
            continue

        image_path = ROOT / subset.iloc[0]["image_path"]

        try:
            with Image.open(image_path) as img:
                image = ImageOps.exif_transpose(img)
                image = image.convert("RGB")
                ax.imshow(image)

        except (OSError, ValueError):
            ax.text(
                0.5, 0.5,
                "Image illisible",
                ha="center",
                va="center",
                transform=ax.transAxes
            )

    for ax in axes[len(variantes):]:
        ax.axis("off")

    fig.suptitle(
        "Échantillons du dataset ACS",
        fontsize=16
    )

    fig.tight_layout()

    fig.savefig(
        OUTPUT_DIR / "echantillons_dataset.png",
        dpi=300
    )

    plt.close(fig)


# Statistiques générales
def print_statistics(df, config):

    print("\n=== Statistiques générales ===")

    print(f"Images analysées : {len(df)}")

    print(f"Types définis : {len(config['types'])}")

    n_variantes = sum(
        len(couleurs)
        for couleurs in config["variantes"].values()
    )

    print(f"Variantes définies : {n_variantes}")

    print(
        "Variantes représentées :",
        df.groupby(["type", "couleur"]).ngroups
    )

    print("\nImages par type :")

    print(
        df["type"]
        .value_counts()
        .reindex(config["types"], fill_value=0)
        .to_string()
    )

    print("\nImages par session :")

    print(
        df["session_id"]
        .value_counts()
        .reindex(["S01", "S02", "S03"], fill_value=0)
        .to_string()
    )

    # Doublons exacts
    duplicates = df["sha256"].duplicated().sum()

    print(f"\nDoublons exacts : {duplicates}")

    # Résolutions
    print("\nRésolutions les plus fréquentes :")

    print(
        df.groupby(["width", "height"])
        .size()
        .sort_values(ascending=False)
        .head(5)
        .to_string()
    )

    # Modes de couleur
    print("\nModes d'image :")

    print(df["mode"].value_counts().to_string())

def main():
    df, config = load_data()

    if df.empty:
        print(
            "\nLe dataset est vide."
            "\nAjoutez des photographies et exécutez"
            "\npython src/data/preparation.py"
        )
        return

    print_statistics(df, config)

    plot_types(df, config)
    plot_variantes(df, config)
    plot_sessions(df, config)
    plot_resolution(df)
    plot_samples(df, config)

    print("\nGraphiques générés dans :")
    print(OUTPUT_DIR.relative_to(ROOT))

    print("\nAnalyse terminée !")


if __name__ == "__main__":
    main()
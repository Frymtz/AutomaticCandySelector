from pathlib import Path
import yaml

ROOT = Path(__file__).resolve().parents[1]

config_path = ROOT / "configs" / "classes.yaml"

with open(config_path, "r", encoding="utf-8") as file:
    config = yaml.safe_load(file)

types = config["types"]
couleurs = config["couleurs"]
variantes = config["variantes"]

assert len(types) == len(set(types)), "Types dupliqués"
assert len(couleurs) == len(set(couleurs)), "Couleurs dupliquées"
assert set(types) == set(variantes.keys())

for type_bonbon, liste_couleurs in variantes.items():

    assert len(liste_couleurs) == len(set(liste_couleurs))

    for couleur in liste_couleurs:
        assert couleur in couleurs, (
            f"Couleur inconnue : {couleur}"
        )

n_types = len(types)

n_couleurs = len(couleurs)

n_variantes = sum(
    len(liste) for liste in variantes.values()
)

print("=== ACS - Configuration des classes ===")

print(f"Nombre de types : {n_types}")
print(f"Nombre d'étiquettes de couleur : {n_couleurs}")
print(f"Nombre de variantes : {n_variantes}")

print("\nClasses disponibles :")

for type_bonbon, liste in variantes.items():
    print(f"{type_bonbon}: {', '.join(liste)}")

print("\nConfiguration valide !")
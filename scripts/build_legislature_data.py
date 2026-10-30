"""Construit les index `src/assemblee_mcp/data/legislature_<n>.json` des législatures closes.

CIVIX publie les scrutins et les votes nominatifs des 14e, 15e et 16e législatures, mais pas
leurs députés (`/deputes?legislature=16` est vide, `/deputes/<uid>` répond 404) ni, avant la 16e,
leurs groupes. On en garde un index compact tiré des données ouvertes de l'Assemblée nationale :
pour chaque député, identifiant, prénom, nom, département, circonscription et périodes
d'appartenance aux groupes ; pour chaque groupe, sigle et nom.

Le script ne tourne jamais en production : il sert à reproduire ou à mettre à jour les fichiers
embarqués, qui sont versionnés.

Usage : python scripts/build_legislature_data.py AMO_JSON_DIR SORTIE_DIR [LÉGISLATURE...]
- AMO_JSON_DIR : dossier `json` de l'archive « AMO30 tous acteurs, tous mandats, tous organes,
  historique » (`ARCHIVE_URL`, environ 14 Mo), qui contient `acteur/` et `organe/` ;
- SORTIE_DIR : dossier où écrire les fichiers (`src/assemblee_mcp/data`) ;
- LÉGISLATURE : numéros à construire (14 15 16 par défaut).
"""

import json
import sys
from pathlib import Path
from typing import Any

ARCHIVE_URL = (
    "https://data.assemblee-nationale.fr/static/openData/repository/17/amo/"
    "tous_acteurs_mandats_organes_xi_legislature/"
    "AMO30_tous_acteurs_tous_mandats_tous_organes_historique.json.zip"
)
DEFAULT_LEGISLATURES = (14, 15, 16)
ASSEMBLY_TYPE = "ASSEMBLEE"
GROUP_TYPE = "GP"
SOURCE = (
    "Données ouvertes de l'Assemblée nationale (AMO30, acteurs, mandats et organes, "
    "historique), Licence Ouverte 2.0"
)


def as_list(value: Any) -> list[Any]:
    """Les champs répétables de l'AMO valent un objet seul ou une liste."""
    if value is None:
        return []
    return value if isinstance(value, list) else [value]


def read_groups(organes_dir: Path, legislature: int) -> dict[str, dict[str, str]]:
    """Sigle et nom des groupes parlementaires de la législature."""
    groups: dict[str, dict[str, str]] = {}
    for path in sorted(organes_dir.glob("PO*.json")):
        organe = json.loads(path.read_text(encoding="utf-8"))["organe"]
        if organe["codeType"] == GROUP_TYPE and organe.get("legislature") == str(legislature):
            groups[organe["uid"]] = {"abbr": organe["libelleAbrev"], "libelle": organe["libelle"]}
    return groups


def deputy_row(acteur: dict[str, Any], legislature: int) -> list[Any] | None:
    """`[uid, prénom, nom, département, circo, [[groupe, début, fin], …]]`, ou `None`.

    Les périodes d'appartenance aux groupes sont triées par date de début ; `fin` vaut `None`
    pour un mandat de groupe sans date de fin.
    """
    mandats = [
        mandat
        for mandat in as_list(acteur["mandats"]["mandat"])
        if mandat.get("legislature") == str(legislature)
    ]
    seats = [mandat for mandat in mandats if mandat["typeOrgane"] == ASSEMBLY_TYPE]
    if not seats:
        return None
    seat = max(seats, key=lambda mandat: mandat["dateDebut"])
    place = (seat.get("election") or {}).get("lieu") or {}
    groups = sorted(
        (mandat for mandat in mandats if mandat["typeOrgane"] == GROUP_TYPE),
        key=lambda mandat: mandat["dateDebut"],
    )
    ident = acteur["etatCivil"]["ident"]
    circo = place.get("numCirco")
    return [
        acteur["uid"]["#text"],
        ident["prenom"],
        ident["nom"],
        place.get("departement"),
        int(circo) if circo else None,
        [
            [mandat["organes"]["organeRef"], mandat["dateDebut"], mandat.get("dateFin")]
            for mandat in groups
        ],
    ]


def read_deputes(acteurs_dir: Path, legislature: int) -> list[list[Any]]:
    """Députés ayant siégé dans la législature, triés par nom puis prénom."""
    rows: list[list[Any]] = []
    for path in sorted(acteurs_dir.glob("PA*.json")):
        row = deputy_row(json.loads(path.read_text(encoding="utf-8"))["acteur"], legislature)
        if row is not None:
            rows.append(row)
    return sorted(rows, key=lambda row: (row[2].casefold(), row[1].casefold(), row[0]))


def main(arguments: list[str]) -> None:
    """Écrit un index JSON par législature demandée."""
    amo_dir, output_dir = Path(arguments[0]), Path(arguments[1])
    legislatures = [int(number) for number in arguments[2:]] or list(DEFAULT_LEGISLATURES)
    for legislature in legislatures:
        groupes = read_groups(amo_dir / "organe", legislature)
        deputes = read_deputes(amo_dir / "acteur", legislature)
        document = {
            "legislature": legislature,
            "source": SOURCE,
            "groupes": groupes,
            "deputes": deputes,
        }
        path = output_dir / f"legislature_{legislature}.json"
        text = json.dumps(document, ensure_ascii=False, separators=(",", ":"))
        path.write_text(text + "\n", encoding="utf-8")
        print(f"{path} : {len(deputes)} députés, {len(groupes)} groupes")


if __name__ == "__main__":
    main(sys.argv[1:])

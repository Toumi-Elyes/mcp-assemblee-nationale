"""Construit `src/assemblee_mcp/data/scrutins_<n>.json.gz` pour les 14e et 15e législatures.

CIVIX publie les scrutins de ces législatures sans titre, sans résultat ni décompte par groupe.
L'Assemblée nationale les publie dans ses archives de scrutins : on en garde, pour chaque
scrutin, la date, le titre, le résultat, le type de vote, la majorité requise, le demandeur, le
décompte officiel global et le décompte par groupe (groupes sans aucun vote exclus). Le fichier
est compressé avec une date fixe pour que deux constructions identiques donnent le même fichier.

Le script ne tourne jamais en production : il sert à reproduire ou à mettre à jour les fichiers
embarqués, qui sont versionnés.

Usage : python scripts/build_scrutin_data.py SCRUTINS_14_JSON SCRUTINS_15_DIR SORTIE_DIR
- SCRUTINS_14_JSON : `Scrutins_XIV.json`, extrait de `ARCHIVE_URLS[14]` ;
- SCRUTINS_15_DIR : dossier `json` extrait de `ARCHIVE_URLS[15]` (un fichier par scrutin) ;
- SORTIE_DIR : dossier où écrire les fichiers (`src/assemblee_mcp/data`).
"""

import gzip
import json
import sys
from collections.abc import Iterable
from pathlib import Path
from typing import Any

REPOSITORY = "https://data.assemblee-nationale.fr/static/openData/repository"
ARCHIVE_URLS = {
    14: f"{REPOSITORY}/14/loi/scrutins/Scrutins_XIV.json.zip",
    15: f"{REPOSITORY}/15/loi/scrutins/Scrutins_XV.json.zip",
}
SOURCE = "Données ouvertes de l'Assemblée nationale (archives des scrutins), Licence Ouverte 2.0"
DISSIDENTS_ONLY = "DecompteDissidentsPositionGroupe"
# Les archives n'écrivent pas les décomptes de la même façon selon la législature.
ABSTENTION_KEYS = ("abstentions", "abstention")
NON_VOTANT_KEYS = ("nonVotants", "nonVotant")


def as_list(value: Any) -> list[Any]:
    """Les champs répétables des archives valent un objet seul ou une liste."""
    if value is None:
        return []
    return value if isinstance(value, list) else [value]


def count(decompte: dict[str, Any], *keys: str) -> int:
    """Premier décompte renseigné parmi `keys`, 0 sinon."""
    for key in keys:
        if decompte.get(key) is not None:
            return int(decompte[key])
    return 0


def group_rows(scrutin: dict[str, Any]) -> list[list[Any]]:
    """`[[groupe, pour, contre, abstention, non_votant], …]`, groupes sans vote exclus."""
    rows: list[list[Any]] = []
    for groupe in as_list(scrutin["ventilationVotes"]["organe"]["groupes"]["groupe"]):
        decompte = groupe["vote"]["decompteVoix"]
        row = [
            groupe["organeRef"],
            count(decompte, "pour"),
            count(decompte, "contre"),
            count(decompte, *ABSTENTION_KEYS),
            count(decompte, *NON_VOTANT_KEYS),
        ]
        if any(row[1:]):
            rows.append(row)
    return rows


def global_counts(scrutin: dict[str, Any]) -> list[int]:
    """Décompte officiel `[pour, contre, abstention, non_votant]` de la synthèse du vote.

    Pour certains scrutins de 2012, les votes nominatifs publiés sont incomplets : la synthèse
    fait foi, et c'est celle que l'Assemblée affiche.
    """
    decompte = scrutin["syntheseVote"]["decompte"]
    return [
        count(decompte, "pour"),
        count(decompte, "contre"),
        count(decompte, *ABSTENTION_KEYS),
        count(decompte, *NON_VOTANT_KEYS),
    ]


def scrutin_row(scrutin: dict[str, Any]) -> list[Any]:
    """`[date, titre, résultat, type, majorité, demandeur, partiel, global, groupes]`.

    `partiel` est vrai quand l'Assemblée n'a publié que les noms des députés ayant voté autrement
    que la position de leur groupe (710 scrutins de la 14e législature, jusqu'en février 2014).
    """
    type_vote = scrutin["typeVote"]
    return [
        scrutin["dateScrutin"],
        scrutin["titre"],
        scrutin["sort"]["code"],
        type_vote["libelleTypeVote"],
        type_vote["typeMajorite"],
        (scrutin.get("demandeur") or {}).get("texte"),
        scrutin.get("modePublicationDesVotes") == DISSIDENTS_ONLY,
        global_counts(scrutin),
        group_rows(scrutin),
    ]


def build_document(legislature: int, scrutins: Iterable[dict[str, Any]]) -> dict[str, Any]:
    """Document d'une législature : identifiant de scrutin vers sa ligne."""
    rows = {scrutin["uid"]: scrutin_row(scrutin) for scrutin in scrutins}
    return {"legislature": legislature, "source": SOURCE, "scrutins": dict(sorted(rows.items()))}


def write_document(document: dict[str, Any], output_dir: Path) -> Path:
    """Écrit le document compressé, de façon reproductible."""
    path = output_dir / f"scrutins_{document['legislature']}.json.gz"
    text = json.dumps(document, ensure_ascii=False, separators=(",", ":"))
    path.write_bytes(gzip.compress(text.encode("utf-8"), mtime=0))
    return path


def main(arguments: list[str]) -> None:
    """Écrit les fichiers des 14e et 15e législatures."""
    file_14, dir_15, output_dir = (Path(argument) for argument in arguments)
    sources = {
        14: json.loads(file_14.read_text(encoding="utf-8"))["scrutins"]["scrutin"],
        15: [
            json.loads(path.read_text(encoding="utf-8"))["scrutin"]
            for path in sorted(dir_15.glob("VTANR5L15V*.json"))
        ],
    }
    for legislature, scrutins in sources.items():
        document = build_document(legislature, scrutins)
        path = write_document(document, output_dir)
        print(f"{path} : {len(document['scrutins'])} scrutins")


if __name__ == "__main__":
    main(sys.argv[1:])

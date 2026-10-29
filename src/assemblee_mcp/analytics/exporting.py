"""Exports machine-lisibles (CSV, JSON) de scrutins et de votes, sans interprétation."""

import csv
import io
import json
from collections.abc import Sequence

from assemblee_mcp.analytics.stats import day_of
from assemblee_mcp.civix.models import ScrutinSummary, Vote
from assemblee_mcp.formatting import sanitize
from assemblee_mcp.links import civix_scrutin_url

Cell = str | int | bool | None
Row = dict[str, Cell]
FORMULA_PREFIXES = ("=", "+", "-", "@")
SCRUTIN_COLUMNS = (
    "uid",
    "numero",
    "date",
    "legislature",
    "type",
    "contexte",
    "resultat",
    "titre",
    "dossier_ref",
    "dossier_libelle",
    "url_civix",
)
VOTE_COLUMNS = (
    "scrutin_uid",
    "depute_uid",
    "prenom",
    "nom",
    "groupe",
    "position",
    "par_delegation",
)


def clean_cell(value: Cell) -> Cell:
    """Retire les caractères de contrôle ou invisibles d'un texte."""
    return sanitize(value) if isinstance(value, str) else value


def csv_cell(value: Cell) -> str:
    """Cellule CSV : neutralise les formules de tableur (`=`, `+`, `-`, `@`)."""
    if value is None:
        return ""
    text = str(clean_cell(value))
    return f"'{text}" if text.startswith(FORMULA_PREFIXES) else text


def scrutin_row(item: ScrutinSummary) -> Row:
    """Ligne d'export d'un scrutin."""
    day = day_of(item)
    return {
        "uid": item.uid,
        "numero": item.numero,
        "date": day.isoformat() if day else None,
        "legislature": item.legislature,
        "type": item.kind,
        "contexte": item.context,
        "resultat": item.sort_code or (item.sort.code if item.sort else None),
        "titre": item.titre,
        "dossier_ref": item.dossier_ref,
        "dossier_libelle": item.dossier_libelle,
        "url_civix": civix_scrutin_url(item.uid),
    }


def vote_row(scrutin_uid: str, vote: Vote, groupe: str | None = None) -> Row:
    """Ligne d'export d'un vote individuel ; `groupe` est le sigle du groupe du député."""
    return {
        "scrutin_uid": scrutin_uid,
        "depute_uid": vote.deputy_uid,
        "prenom": vote.prenom,
        "nom": vote.nom,
        "groupe": groupe,
        "position": vote.position.value,
        "par_delegation": vote.par_delegation,
    }


def to_csv(columns: Sequence[str], rows: Sequence[Row]) -> str:
    """CSV avec en-tête (séparateur virgule, lignes terminées par un saut de ligne)."""
    buffer = io.StringIO()
    writer = csv.writer(buffer, lineterminator="\n")
    writer.writerow(columns)
    for row in rows:
        writer.writerow([csv_cell(row.get(column)) for column in columns])
    return buffer.getvalue().rstrip("\n")


def to_json(columns: Sequence[str], rows: Sequence[Row]) -> str:
    """Tableau JSON d'objets, avec les clés dans l'ordre des colonnes."""
    cleaned = [{column: clean_cell(row.get(column)) for column in columns} for row in rows]
    return json.dumps(cleaned, ensure_ascii=False)


def serialise(format_name: str, columns: Sequence[str], rows: Sequence[Row]) -> str:
    """Sérialise en `csv` ou `json`."""
    return to_json(columns, rows) if format_name == "json" else to_csv(columns, rows)

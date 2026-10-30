"""Script de construction des index des législatures closes, sur une mini archive AMO."""

import importlib.util
import json
from pathlib import Path
from types import ModuleType
from typing import Any

from assemblee_mcp.civix.archive import build_depute, build_memberships
from assemblee_mcp.civix.models import Groupe

SCRIPT = Path(__file__).parent.parent / "scripts" / "build_legislature_data.py"


def load_script() -> ModuleType:
    spec = importlib.util.spec_from_file_location("build_legislature_data", SCRIPT)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def mandat(legislature: str, kind: str, organe: str, start: str, end: str | None) -> Any:
    seat = {"lieu": {"departement": "Nord", "numCirco": "16"}} if kind == "ASSEMBLEE" else None
    return {
        "legislature": legislature,
        "typeOrgane": kind,
        "organes": {"organeRef": organe},
        "dateDebut": start,
        "dateFin": end,
        "election": seat,
    }


def write_amo(root: Path) -> None:
    (root / "acteur").mkdir(parents=True)
    (root / "organe").mkdir()
    acteurs = {
        "PA1": (
            "Alain",
            "Bruneel",
            [
                mandat("15", "ASSEMBLEE", "PO717460", "2017-06-18", "2022-06-21"),
                mandat("15", "GP", "PO730940", "2017-06-27", "2022-06-21"),
                mandat("15", "GP", "PO723569", "2017-06-21", "2017-06-26"),
                mandat("16", "GP", "PO800502", "2022-06-22", None),
            ],
        ),
        "PA2": ("Seul", "Mandat", mandat("14", "ASSEMBLEE", "PO644420", "2012-06-20", None)),
    }
    for uid, (first, last, mandats) in acteurs.items():
        acteur = {
            "uid": {"#text": uid},
            "etatCivil": {"ident": {"prenom": first, "nom": last}},
            "mandats": {"mandat": mandats},
        }
        (root / "acteur" / f"{uid}.json").write_text(json.dumps({"acteur": acteur}), "utf-8")
    organes = [
        ("PO730940", "GP", "15", "GDR", "Gauche démocrate et républicaine"),
        ("PO723569", "GP", "15", "NI", "Non inscrit"),
        ("PO717460", "ASSEMBLEE", "15", "AN", "Assemblée nationale"),
        ("PO800502", "GP", "16", "GDR-NUPES", "Gauche démocrate et républicaine - NUPES"),
    ]
    for uid, kind, legislature, abbr, libelle in organes:
        organe = {
            "uid": uid,
            "codeType": kind,
            "legislature": legislature,
            "libelleAbrev": abbr,
            "libelle": libelle,
        }
        (root / "organe" / f"{uid}.json").write_text(json.dumps({"organe": organe}), "utf-8")


def test_script_builds_an_index_the_server_can_read(tmp_path: Path) -> None:
    amo, output = tmp_path / "json", tmp_path / "data"
    write_amo(amo)
    output.mkdir()
    load_script().main([str(amo), str(output), "15"])

    document = json.loads((output / "legislature_15.json").read_text("utf-8"))
    assert document["legislature"] == 15
    assert set(document["groupes"]) == {"PO730940", "PO723569"}
    assert document["deputes"] == [
        [
            "PA1",
            "Alain",
            "Bruneel",
            "Nord",
            16,
            [["PO723569", "2017-06-21", "2017-06-26"], ["PO730940", "2017-06-27", "2022-06-21"]],
        ]
    ]
    groupes = load_script().read_groups(amo / "organe", 15)
    row = document["deputes"][0]
    assert len(build_memberships(row[5])) == 2
    known = {
        uid: Groupe(uid=uid, abbr=item["abbr"], libelle=item["libelle"])
        for uid, item in groupes.items()
    }
    depute = build_depute(row, known, 15)
    assert (depute.groupe_abrev, depute.circ_departement, depute.circ_num) == ("GDR", "Nord", 16)


def test_script_skips_deputies_without_a_seat_in_the_legislature(tmp_path: Path) -> None:
    amo = tmp_path / "json"
    write_amo(amo)
    rows = load_script().read_deputes(amo / "acteur", 14)
    assert [row[0] for row in rows] == ["PA2"]
    assert rows[0][3:] == ["Nord", 16, []]

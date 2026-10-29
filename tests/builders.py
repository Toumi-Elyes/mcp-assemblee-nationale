"""Fabriques de petits modèles CIVIX pour les tests de calcul, sans réseau ni fixture JSON."""

from assemblee_mcp.civix.models import ScrutinSummary, ScrutinVotes
from tests.conftest import make_item

ABBREVIATIONS = {"G1": "AAA", "G2": "BBB", "G3": "CCC"}


def summary(number: int, day: str, **kwargs: object) -> ScrutinSummary:
    return ScrutinSummary.model_validate(make_item(number, day, **kwargs))  # type: ignore[arg-type]


def group_counts(**counts: tuple[int, int, int]) -> list[dict[str, object]]:
    return [
        {
            "groupe_uid": uid,
            "pour": pour,
            "contre": contre,
            "abstention": abstention,
            "non_votant": 0,
            "total": pour + contre + abstention,
        }
        for uid, (pour, contre, abstention) in counts.items()
    ]


def scrutin_votes(
    number: int, by_group: list[dict[str, object]], votes: list[dict[str, object]] | None = None
) -> ScrutinVotes:
    total = [sum(int(str(g[key])) for g in by_group) for key in ("pour", "contre", "abstention")]
    return ScrutinVotes.model_validate(
        {
            "scrutin": {
                "uid": f"U{number}",
                "numero": number,
                "date_scrutin": "2026-10-01T00:00:00+00:00",
                "titre": f"scrutin {number}",
                "sort_libelle": "adopté",
            },
            "results_global": {
                "pour": total[0],
                "contre": total[1],
                "abstention": total[2],
                "total": sum(total),
            },
            "results_by_group": by_group,
            "votes": votes or [],
        }
    )


def vote_entry(uid: str, position: str, *, delegated: bool = False) -> dict[str, object]:
    return {
        "deputy_uid": uid,
        "prenom": "A",
        "nom": uid,
        "position": position,
        "par_delegation": delegated,
    }

"""Mise en forme des votes individuels d'un scrutin, regroupés par position."""

from collections.abc import Sequence
from dataclasses import dataclass

from assemblee_mcp.civix.models import (
    CivixResponse,
    Position,
    ScrutinVotes,
    Vote,
)
from assemblee_mcp.formatting.scrutins import counts_sentence, scrutin_heading
from assemblee_mcp.formatting.sources import finish, scrutin_source_line
from assemblee_mcp.formatting.text import field_text
from assemblee_mcp.textutils import fold

MAX_VOTE_NAMES = 60

POSITION_ORDER = (
    Position.POUR,
    Position.CONTRE,
    Position.ABSTENTION,
    Position.NON_VOTANT,
    Position.UNKNOWN,
)


def select_votes(
    votes: Sequence[Vote],
    *,
    member_uids: set[str] | None = None,
    position: Position | None = None,
    nom: str | None = None,
) -> list[Vote]:
    """Filtre les votes par groupe (via ses membres), position et nom (sans accents)."""
    wanted_name = fold(nom) if nom else None
    return [
        vote
        for vote in votes
        if (member_uids is None or vote.deputy_uid in member_uids)
        and (position is None or vote.position == position)
        and (wanted_name is None or wanted_name in fold(vote.full_name))
    ]


@dataclass(frozen=True)
class VoteFilters:
    """Filtres appliqués à la liste des votes, pour les rappeler dans la réponse."""

    groupe: str | None = None
    position: Position | None = None
    nom: str | None = None

    def describe(self) -> str | None:
        """Phrase décrivant les filtres actifs."""
        parts = []
        if self.groupe:
            parts.append(f"groupe {self.groupe} (groupe actuel des députés)")
        if self.position:
            parts.append(f"position « {self.position.label} »")
        if self.nom:
            parts.append(f"nom contenant « {self.nom} »")
        return ", ".join(parts) if parts else None


def vote_names(votes: Sequence[Vote]) -> list[str]:
    """Noms triés, avec la mention « par délégation »."""
    ordered = sorted(votes, key=lambda vote: fold(f"{vote.nom} {vote.prenom}"))
    return [
        field_text(vote.full_name) + (" (par délégation)" if vote.par_delegation else "")
        for vote in ordered
    ]


def format_votes(
    response: CivixResponse[ScrutinVotes],
    selected: Sequence[Vote],
    filters: VoteFilters,
    limit: int = MAX_VOTE_NAMES,
) -> str:
    """Votes individuels regroupés par position, avec totaux et plafond de noms."""
    attributes = response.attributes
    scrutin = attributes.scrutin
    lines = [scrutin_heading(scrutin), ""]
    if attributes.results_global is not None:
        lines.append(f"Décompte officiel : {counts_sentence(attributes.results_global)}.")
    description = filters.describe()
    recorded = len(attributes.votes)
    if description:
        lines.append(
            f"Filtre : {description} → {len(selected)} vote(s) sur {recorded} votes individuels."
        )
    else:
        lines.append(f"{recorded} votes individuels enregistrés.")
    budget = limit
    for position in POSITION_ORDER:
        group = [vote for vote in selected if vote.position == position]
        if not group:
            continue
        names = vote_names(group)
        shown = names[:budget]
        budget -= len(shown)
        lines += ["", f"### {position.label} ({len(group)})"]
        if shown:
            lines.append(", ".join(shown))
        if len(shown) < len(names):
            lines.append(f"… et {len(names) - len(shown)} autres.")
    if not selected:
        lines += ["", "Aucun vote ne correspond à ces critères."]
    elif len(selected) > limit:
        lines += ["", "Affinez avec `groupe`, `position` ou `nom` pour voir les autres noms."]
    return finish("\n".join(lines), scrutin_source_line(scrutin))

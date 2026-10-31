"""Mise en forme des scrutins : listes et fiches détaillées avec décomptes."""

from collections.abc import Mapping, Sequence

from assemblee_mcp.civix.models import (
    CivixResponse,
    GroupVoteCounts,
    Scrutin,
    ScrutinDetail,
    ScrutinSummary,
    VoteCounts,
)
from assemblee_mcp.civix.scrutin_archive import ARCHIVE_SOURCE
from assemblee_mcp.civix.search import ScrutinSearch
from assemblee_mcp.formatting.sources import (
    finish,
    pagination_hint,
    response_source_line,
    scrutin_source_line,
    source_line,
)
from assemblee_mcp.formatting.text import field_text, format_date, truncate
from assemblee_mcp.links import scrutin_page_url

UNTITLED = "(titre non fourni par CIVIX)"
ARCHIVED_NOTE = (
    "_Titre, résultat et décomptes : archive des scrutins de l'Assemblée nationale ({url}), "
    "CIVIX ne les publiant pas pour cette législature._"
)


def counts_sentence(counts: VoteCounts) -> str:
    """Décompte en une phrase."""
    parts = [
        f"{counts.pour} pour",
        f"{counts.contre} contre",
        f"{counts.abstention} abstention(s)",
        f"{counts.non_votant} non-votant(s)",
    ]
    if counts.unknown:
        parts.append(f"{counts.unknown} inconnu(s)")
    return ", ".join(parts) + f" (total {counts.total})"


def result_label(scrutin: ScrutinSummary | ScrutinDetail) -> str:
    """Résultat officiel d'un scrutin."""
    if isinstance(scrutin, ScrutinDetail):
        return field_text(scrutin.result_label or "résultat non précisé")
    if scrutin.sort is None:
        return "résultat non précisé"
    return field_text(scrutin.sort.libelle or scrutin.sort.code or "résultat non précisé")


def scrutin_line(scrutin: ScrutinSummary) -> str:
    """Ligne de liste pour un scrutin."""
    number = f"n°{scrutin.numero}" if scrutin.numero is not None else ""
    head = " · ".join(
        part for part in (format_date(scrutin.date_scrutin), number, result_label(scrutin)) if part
    )
    title = truncate(scrutin.titre) or UNTITLED
    link = scrutin_page_url(scrutin.uid, scrutin.legislature, scrutin.numero)
    return f"- {head}\n  {title}\n  uid : `{scrutin.uid}` · {link}"


def format_scrutin_list(search: ScrutinSearch, query: str | None) -> str:
    """Liste de scrutins, avec la mention d'une éventuelle recherche élargie."""
    results = search.results
    subject = f" pour « {query} »" if query else ""
    source = (
        response_source_line(search.response)
        if search.response is not None
        else source_line(None, ARCHIVE_SOURCE)
    )
    note = f"_{search.note}_\n\n" if search.note else ""
    if not results:
        body = (
            f"{note}Aucun scrutin trouvé{subject}. Essayez d'autres mots-clés, au singulier, "
            "avec les accents français (« chômage », pas « chomage »)."
        )
        return finish(body, source)
    lines = "\n".join(scrutin_line(scrutin) for scrutin in results)
    hint = pagination_hint(search.pagination, len(results), "scrutin(s)")
    follow = "Pour le détail ou les votes d'un scrutin, utilisez son `uid`."
    body = f"## Scrutins{subject}\n\n{note}{lines}\n\n{hint}\n{follow}"
    return finish(body, source)


def group_label(uid: str, abbreviations: Mapping[str, str]) -> str:
    """Sigle du groupe, ou son identifiant s'il est inconnu."""
    return abbreviations.get(uid, uid)


def group_counts_table(rows: Sequence[GroupVoteCounts], abbreviations: Mapping[str, str]) -> str:
    """Tableau des décomptes par groupe."""
    header = (
        "| Groupe | Pour | Contre | Abstention | Non-votant | Total |\n|---|---|---|---|---|---|"
    )
    body = "\n".join(
        f"| {group_label(row.groupe_uid, abbreviations)} | {row.pour} | {row.contre} | "
        f"{row.abstention} | {row.non_votant} | {row.total} |"
        for row in sorted(rows, key=lambda row: group_label(row.groupe_uid, abbreviations))
    )
    return f"{header}\n{body}"


def scrutin_facts(scrutin: ScrutinDetail) -> list[str]:
    """Faits d'en-tête d'un scrutin sous forme de puces."""
    facts = [f"- Résultat officiel : {result_label(scrutin)}"]
    if scrutin.type_vote and scrutin.type_vote.libelle:
        majority = scrutin.type_vote.type_majorite
        facts.append(
            f"- Type de vote : {field_text(scrutin.type_vote.libelle)}"
            + (f" ({field_text(majority)})" if majority else "")
        )
    if scrutin.majority_rule:
        facts.append(f"- Règle de majorité : {field_text(scrutin.majority_rule)}")
    if scrutin.legislature is not None:
        facts.append(f"- Législature : {scrutin.legislature}")
    dossier = scrutin.objet.dossier_legislatif if scrutin.objet else None
    if dossier and dossier.libelle:
        facts.append(f"- Dossier législatif : {field_text(dossier.libelle)}")
    if scrutin.demandeur and scrutin.demandeur.texte:
        facts.append(f"- Demandé par : {field_text(scrutin.demandeur.texte)}")
    return facts


def scrutin_heading(scrutin: ScrutinDetail) -> str:
    """Titre markdown d'un scrutin."""
    number = f" n°{scrutin.numero}" if scrutin.numero is not None else ""
    title = truncate(scrutin.titre, 600)
    return f"## Scrutin{number} — {format_date(scrutin.date_scrutin)}\n\n{title}"


def format_scrutin(
    response: CivixResponse[Scrutin], abbreviations: Mapping[str, str] | None = None
) -> str:
    """Détail d'un scrutin avec décomptes global et par groupe."""
    attributes = response.attributes
    scrutin = attributes.scrutin
    lines = [scrutin_heading(scrutin), "", *scrutin_facts(scrutin)]
    if attributes.results_global is not None:
        lines.append(f"- Décompte : {counts_sentence(attributes.results_global)}")
    lines.append(f"- Identifiant : `{scrutin.uid}`")
    if attributes.results_by_group:
        lines += ["", "### Décompte par groupe", ""]
        lines.append(group_counts_table(attributes.results_by_group, abbreviations or {}))
    if attributes.archived:
        lines += ["", ARCHIVED_NOTE.format(url=ARCHIVE_SOURCE)]
    lines += ["", "Pour savoir qui a voté quoi, utilisez `votes_scrutin` avec cet identifiant."]
    return finish("\n".join(lines), scrutin_source_line(scrutin))

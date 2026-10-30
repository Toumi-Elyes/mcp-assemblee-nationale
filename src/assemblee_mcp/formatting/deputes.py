"""Mise en forme des députés et de leurs positions sur des scrutins."""

from collections.abc import Sequence
from dataclasses import dataclass
from datetime import datetime

from assemblee_mcp.civix.archive import ARCHIVED_LEGISLATURES, covered_legislatures
from assemblee_mcp.civix.models import (
    CivixResponse,
    Depute,
    DeputeDetail,
    ScrutinSummary,
    ScrutinVotes,
    Vote,
)
from assemblee_mcp.formatting.scrutins import result_label
from assemblee_mcp.formatting.sources import finish, source_line
from assemblee_mcp.formatting.text import field_text, format_date, truncate
from assemblee_mcp.links import (
    assemblee_scrutin_url,
    civix_scrutin_url,
    depute_assemblee_url,
    depute_civix_url,
)


def depute_page_url(depute: Depute) -> str:
    """Page CIVIX d'un député en cours de mandat ; page Assemblée pour une législature close.

    CIVIX n'a pas de fiche pour les députés des législatures closes (`/deputes/<uid>` : 404).
    """
    if depute.legislature in ARCHIVED_LEGISLATURES:
        return depute_assemblee_url(depute)
    return depute_civix_url(depute)


def depute_source_line(depute: Depute) -> str:
    """Ligne « Source : » d'un député, sans lien CIVIX pour une législature close."""
    civix = None if depute.legislature in ARCHIVED_LEGISLATURES else depute_civix_url(depute)
    return source_line(civix, depute_assemblee_url(depute))


def depute_line(depute: Depute) -> str:
    """Ligne de liste pour un député."""
    where = []
    if depute.groupe_abrev:
        where.append(depute.groupe_abrev)
    if depute.circ_departement:
        circ = f" ({depute.circ_num}e circ.)" if depute.circ_num is not None else ""
        where.append(f"{depute.circ_departement}{circ}")
    place = " · ".join(where)
    return (
        f"- **{field_text(depute.full_name)}**"
        + (f" — {place}" if place else "")
        + f"\n  uid : `{depute.uid}`"
        f" · {depute_page_url(depute)}"
    )


ARCHIVE_CARD_NOTE = (
    "- Député de la {legislature}e législature (données ouvertes de l'Assemblée nationale) : "
    "le groupe indiqué est son dernier groupe dans cette législature."
)


def format_deputes(deputes: Sequence[Depute], title: str, hint: str = "") -> str:
    """Liste de députés."""
    if not deputes:
        body = (
            f"{title} : aucun député trouvé. Vérifiez l'orthographe du nom ; "
            f"seuls les députés des législatures {covered_legislatures()} sont couverts."
            + (f"\n\n{hint}" if hint else "")
        )
        return finish(body, source_line("https://www.civix.fr/deputes", None))
    lines = "\n".join(depute_line(depute) for depute in deputes)
    body = f"## {title}\n\n{lines}" + (f"\n\n{hint}" if hint else "")
    body += "\n\nPour le détail d'un député, utilisez `obtenir_depute` avec son `uid`."
    return finish(body, source_line("https://www.civix.fr/deputes", None))


def format_depute(response: CivixResponse[DeputeDetail]) -> str:
    """Fiche d'un député de la législature en cours, d'après la réponse CIVIX."""
    return format_depute_card(response.attributes.deputy)


def format_depute_card(depute: Depute) -> str:
    """Fiche d'un député ; pour une législature close, précise ce que l'index ne contient pas."""
    lines = [f"## {field_text(depute.full_name)}", ""]
    if depute.groupe_libelle or depute.groupe_abrev:
        lines.append(
            f"- Groupe : {field_text(depute.groupe_libelle or '')} "
            f"({field_text(depute.groupe_abrev or '?')})".replace(" ()", "")
        )
    if depute.circ_departement:
        circ = f", {depute.circ_num}e circonscription" if depute.circ_num is not None else ""
        lines.append(f"- Circonscription : {depute.circ_departement}{circ}")
    if depute.legislature is not None:
        lines.append(f"- Législature : {depute.legislature}")
    lines.append(f"- Identifiant : `{depute.uid}`")
    if depute.legislature in ARCHIVED_LEGISLATURES:
        lines.append(ARCHIVE_CARD_NOTE.format(legislature=depute.legislature))
    return finish("\n".join(lines), depute_source_line(depute))


@dataclass(frozen=True)
class ScrutinPosition:
    """Position d'un député sur un scrutin, ou raison pour laquelle elle est inconnue."""

    uid: str
    numero: int | None
    titre: str
    date_scrutin: datetime | None
    result: str
    vote: Vote | None
    assemblee_url: str | None = None
    unavailable: bool = False
    dissidents_only: bool = False


def position_from_votes(response: CivixResponse[ScrutinVotes], depute_uid: str) -> ScrutinPosition:
    """Retrouve le vote d'un député dans les votes d'un scrutin."""
    scrutin = response.attributes.scrutin
    vote = next((vote for vote in response.attributes.votes if vote.deputy_uid == depute_uid), None)
    return ScrutinPosition(
        uid=scrutin.uid,
        numero=scrutin.numero,
        titre=scrutin.titre,
        date_scrutin=scrutin.date_scrutin,
        result=result_label(scrutin),
        vote=vote,
        assemblee_url=assemblee_scrutin_url(scrutin.legislature, scrutin.numero),
        dissidents_only=response.attributes.dissidents_only,
    )


def position_unavailable(scrutin: ScrutinSummary) -> ScrutinPosition:
    """Position inconnue car les votes du scrutin n'ont pas pu être récupérés."""
    return ScrutinPosition(
        uid=scrutin.uid,
        numero=scrutin.numero,
        titre=scrutin.titre,
        date_scrutin=scrutin.date_scrutin,
        result=result_label(scrutin),
        vote=None,
        unavailable=True,
    )


def position_sentence(entry: ScrutinPosition) -> str:
    """Position du député sur un scrutin, en une phrase neutre."""
    if entry.unavailable:
        return "Votes de ce scrutin momentanément indisponibles."
    if entry.vote is None and entry.dissidents_only:
        return (
            "Son nom n'apparaît pas : pour ce scrutin, l'Assemblée n'a publié que les noms des "
            "députés ayant voté autrement que leur groupe. Son vote individuel n'est pas connu."
        )
    if entry.vote is None:
        return "Aucun vote enregistré pour ce député sur ce scrutin."
    delegation = " (par délégation)" if entry.vote.par_delegation else ""
    return f"A voté : **{entry.vote.position.label}**{delegation}."


def position_block(entry: ScrutinPosition) -> str:
    """Bloc de réponse pour un scrutin."""
    number = f" n°{entry.numero}" if entry.numero is not None else ""
    links = source_line(civix_scrutin_url(entry.uid), entry.assemblee_url)
    return (
        f"### Scrutin{number} — {format_date(entry.date_scrutin)}\n"
        f"{truncate(entry.titre)}\n"
        f"Résultat officiel : {entry.result}\n"
        f"{position_sentence(entry)}\n"
        f"{links}"
    )


def format_comment_a_vote(depute: Depute, entries: Sequence[ScrutinPosition], pool: str) -> str:
    """Réponse à « Comment a voté X ? » pour une liste de scrutins."""
    blocks = "\n\n".join(position_block(entry) for entry in entries)
    body = (
        f"## Votes de {field_text(depute.full_name)}"
        + (f" ({depute.groupe_abrev})" if depute.groupe_abrev else "")
        + f"\n\n{pool}\n\n{blocks}"
    )
    return finish(body, depute_source_line(depute))


def format_depute_candidates(query: str, candidates: Sequence[Depute], limit: int) -> str:
    """Plusieurs députés correspondent : demande de précision."""
    lines = "\n".join(depute_line(depute) for depute in candidates[:limit])
    more = len(candidates) - limit
    extra = f"\n… et {more} autres." if more > 0 else ""
    body = (
        f"Plusieurs députés correspondent à « {query} ». Lequel voulez-vous dire ?\n\n"
        f"{lines}{extra}\n\n"
        "Redemandez avec le nom complet exact ou l'`uid` du député choisi."
    )
    return finish(body, source_line("https://www.civix.fr/deputes", None))


def format_no_scrutin(subject: str) -> str:
    """Aucun scrutin ne correspond au sujet demandé."""
    body = (
        f"Aucun scrutin trouvé pour « {subject} ». Essayez des mots-clés plus courts, au "
        "singulier, avec les accents français."
    )
    return finish(body, source_line("https://www.civix.fr", None))

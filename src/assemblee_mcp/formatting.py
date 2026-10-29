"""Mise en forme des modèles en markdown français concis, sans interprétation politique."""

from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from datetime import datetime

from assemblee_mcp.civix.models import (
    AttributesT,
    CivixResponse,
    Depute,
    DeputeDetail,
    Groupe,
    GroupeDetail,
    GroupeList,
    GroupeStatement,
    GroupVoteCounts,
    Pagination,
    Position,
    Scrutin,
    ScrutinDetail,
    ScrutinList,
    ScrutinSummary,
    ScrutinVotes,
    SearchResults,
    StatementList,
    Vote,
    VoteCounts,
)
from assemblee_mcp.links import (
    civix_depute_url,
    civix_scrutin_url,
    depute_assemblee_url,
    depute_civix_url,
    groupe_civix_url,
)
from assemblee_mcp.textutils import fold

FOOTER = (
    "_CIVIX est une interface indépendante et non officielle des données ouvertes "
    "de l'Assemblée nationale._"
)
MAX_VOTE_NAMES = 60
MAX_TITLE_LENGTH = 240
MONTHS = (
    "janvier",
    "février",
    "mars",
    "avril",
    "mai",
    "juin",
    "juillet",
    "août",
    "septembre",
    "octobre",
    "novembre",
    "décembre",
)
POSITION_ORDER = (
    Position.POUR,
    Position.CONTRE,
    Position.ABSTENTION,
    Position.NON_VOTANT,
    Position.UNKNOWN,
)


def format_date(value: datetime | None) -> str:
    """Date en français, par exemple « 4 juin 2026 »."""
    if value is None:
        return "date inconnue"
    day = "1er" if value.day == 1 else str(value.day)
    return f"{day} {MONTHS[value.month - 1]} {value.year}"


def truncate(text: str, limit: int = MAX_TITLE_LENGTH) -> str:
    """Raccourcit un texte trop long."""
    clean = " ".join(text.split())
    return clean if len(clean) <= limit else clean[: limit - 1].rstrip() + "…"


def source_line(civix_url: str | None, assemblee_url: str | None) -> str:
    """Ligne « Source : » avec les liens disponibles."""
    parts = []
    if civix_url:
        parts.append(f"CIVIX {civix_url}")
    if assemblee_url:
        parts.append(f"Assemblée nationale {assemblee_url}")
    return "Source : " + (" — ".join(parts) if parts else "CIVIX https://www.civix.fr")


def response_source_line(response: CivixResponse[AttributesT]) -> str:
    """Ligne « Source : » d'une réponse CIVIX."""
    civix = response.source.civix_page or response.canonical_url
    return source_line(civix, response.source.assemblee_url)


def finish(body: str, source: str) -> str:
    """Ajoute la ligne source et le pied de page à un corps de texte."""
    return f"{body}\n\n{source}\n{FOOTER}"


def pagination_hint(pagination: Pagination | None, shown: int, noun: str) -> str:
    """Indique s'il existe d'autres pages et comment les demander."""
    if pagination is None:
        return ""
    total = pagination.total
    count = f"{shown} {noun} affiché(s)" + (f" sur {total}" if total is not None else "")
    if pagination.next_page is None:
        return f"_{count}._"
    return (
        f"_{count} (page {pagination.page or 1}). Il reste des résultats : "
        f"demandez la page {pagination.next_page}._"
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
        return scrutin.result_label or "résultat non précisé"
    if scrutin.sort is None:
        return "résultat non précisé"
    return scrutin.sort.libelle or scrutin.sort.code or "résultat non précisé"


def scrutin_line(scrutin: ScrutinSummary) -> str:
    """Ligne de liste pour un scrutin."""
    number = f"n°{scrutin.numero}" if scrutin.numero is not None else ""
    head = " · ".join(
        part for part in (format_date(scrutin.date_scrutin), number, result_label(scrutin)) if part
    )
    return f"- {head}\n  {truncate(scrutin.titre)}\n  uid : `{scrutin.uid}`"


def format_scrutin_list(response: CivixResponse[ScrutinList], query: str | None) -> str:
    """Liste de scrutins."""
    results = response.attributes.results
    subject = f" pour « {query} »" if query else ""
    if not results:
        body = (
            f"Aucun scrutin trouvé{subject}. Essayez d'autres mots-clés, au singulier, "
            "avec les accents français (« chômage », pas « chomage »)."
        )
        return finish(body, response_source_line(response))
    lines = "\n".join(scrutin_line(scrutin) for scrutin in results)
    hint = pagination_hint(response.pagination, len(results), "scrutin(s)")
    follow = "Pour le détail ou les votes d'un scrutin, utilisez son `uid`."
    body = f"## Scrutins{subject}\n\n{lines}\n\n{hint}\n{follow}"
    return finish(body, response_source_line(response))


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
        for row in sorted(rows, key=lambda r: group_label(r.groupe_uid, abbreviations))
    )
    return f"{header}\n{body}"


def scrutin_facts(scrutin: ScrutinDetail) -> list[str]:
    """Faits d'en-tête d'un scrutin sous forme de puces."""
    facts = [f"- Résultat officiel : {result_label(scrutin)}"]
    if scrutin.type_vote and scrutin.type_vote.libelle:
        majority = scrutin.type_vote.type_majorite
        facts.append(
            f"- Type de vote : {scrutin.type_vote.libelle}" + (f" ({majority})" if majority else "")
        )
    if scrutin.majority_rule:
        facts.append(f"- Règle de majorité : {scrutin.majority_rule}")
    if scrutin.legislature is not None:
        facts.append(f"- Législature : {scrutin.legislature}")
    dossier = scrutin.objet.dossier_legislatif if scrutin.objet else None
    if dossier and dossier.libelle:
        facts.append(f"- Dossier législatif : {dossier.libelle}")
    if scrutin.demandeur and scrutin.demandeur.texte:
        facts.append(f"- Demandé par : {scrutin.demandeur.texte}")
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
    lines += ["", "Pour savoir qui a voté quoi, utilisez `votes_scrutin` avec cet identifiant."]
    return finish("\n".join(lines), response_source_line(response))


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
        vote.full_name + (" (par délégation)" if vote.par_delegation else "") for vote in ordered
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
    return finish("\n".join(lines), response_source_line(response))


def statement_block(statement: GroupeStatement) -> str:
    """Déclaration d'un groupe."""
    name = statement.groupe_abrev or statement.groupe_libelle or "Groupe"
    details = [
        f"position de vote : {statement.vote_position}" if statement.vote_position else "",
        f"opinion : {statement.opinion_code}" if statement.opinion_code else "",
        f"déposée le {format_date(statement.submitted_at)}" if statement.submitted_at else "",
    ]
    meta = " · ".join(part for part in details if part)
    heading = f"**{name}**" + (f" ({meta})" if meta else "")
    return f"{heading}\n> {statement.statement}"


def format_statements(response: CivixResponse[StatementList], uid: str) -> str:
    """Déclarations publiques des groupes sur un scrutin."""
    statements = response.attributes.statements
    if not statements:
        body = (
            f"Aucune déclaration publique de groupe n'est publiée sur CIVIX pour le scrutin "
            f"`{uid}`."
        )
    else:
        blocks = "\n\n".join(statement_block(statement) for statement in statements)
        body = f"## Déclarations des groupes — scrutin `{uid}`\n\n{blocks}"
    return finish(body, source_line(civix_scrutin_url(uid), None))


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
        f"- **{depute.full_name}**" + (f" — {place}" if place else "") + f"\n  uid : `{depute.uid}`"
        f" · {depute_civix_url(depute)}"
    )


def format_deputes(deputes: Sequence[Depute], title: str, hint: str = "") -> str:
    """Liste de députés."""
    if not deputes:
        body = (
            f"{title} : aucun député trouvé. Vérifiez l'orthographe du nom ; "
            "seuls les députés de la législature en cours sont couverts."
        )
        return finish(body, source_line("https://www.civix.fr/deputes", None))
    lines = "\n".join(depute_line(depute) for depute in deputes)
    body = f"## {title}\n\n{lines}" + (f"\n\n{hint}" if hint else "")
    body += "\n\nPour le détail d'un député, utilisez `obtenir_depute` avec son `uid`."
    return finish(body, source_line("https://www.civix.fr/deputes", None))


def format_depute(response: CivixResponse[DeputeDetail]) -> str:
    """Fiche d'un député."""
    depute = response.attributes.deputy
    lines = [f"## {depute.full_name}", ""]
    if depute.groupe_libelle or depute.groupe_abrev:
        lines.append(
            f"- Groupe : {depute.groupe_libelle or ''} ({depute.groupe_abrev or '?'})".replace(
                " ()", ""
            )
        )
    if depute.circ_departement:
        circ = f", {depute.circ_num}e circonscription" if depute.circ_num is not None else ""
        lines.append(f"- Circonscription : {depute.circ_departement}{circ}")
    if depute.legislature is not None:
        lines.append(f"- Législature : {depute.legislature}")
    lines.append(f"- Identifiant : `{depute.uid}`")
    source = source_line(depute_civix_url(depute), depute_assemblee_url(depute))
    return finish("\n".join(lines), source)


def groupe_line(groupe: Groupe) -> str:
    """Ligne de liste pour un groupe."""
    size = f" — {groupe.effectif} député(s)" if groupe.effectif is not None else ""
    return f"- **{groupe.abbr}** : {groupe.libelle}{size}"


def format_groupes(response: CivixResponse[GroupeList]) -> str:
    """Liste des groupes parlementaires."""
    groups = response.attributes.groups
    lines = "\n".join(groupe_line(groupe) for groupe in groups)
    body = f"## Groupes parlementaires ({len(groups)})\n\n{lines}"
    body += "\n\nUtilisez le sigle (par exemple dans `votes_scrutin`) pour filtrer par groupe."
    return finish(body, response_source_line(response))


def format_groupe(response: CivixResponse[GroupeDetail]) -> str:
    """Fiche d'un groupe."""
    groupe = response.attributes.groupe
    lines = [f"## {groupe.libelle} ({groupe.abbr})", ""]
    if groupe.effectif is not None:
        lines.append(f"- Effectif : {groupe.effectif} député(s)")
    if groupe.legislature is not None:
        lines.append(f"- Législature : {groupe.legislature}")
    lines.append(f"- Identifiant : `{groupe.uid}`")
    return finish("\n".join(lines), source_line(groupe_civix_url(groupe), None))


def format_search(response: CivixResponse[SearchResults], query: str) -> str:
    """Résultats de la recherche globale, par catégorie."""
    results = response.attributes.results
    sections: list[str] = []
    if results.scrutins:
        lines = "\n".join(
            f"- {format_date(hit.date_scrutin)} · {truncate(hit.titre, 180)} · uid `{hit.uid}`"
            for hit in results.scrutins
        )
        sections.append(f"### Scrutins\n{lines}")
    if results.deputes:
        lines = "\n".join(
            f"- {hit.prenom} {hit.nom}"
            + (f" ({hit.groupe_abrev})" if hit.groupe_abrev else "")
            + f" · uid `{hit.uid}`"
            for hit in results.deputes
        )
        sections.append(f"### Députés\n{lines}")
    if results.groupes:
        lines = "\n".join(f"- {hit.abbr} : {hit.libelle}" for hit in results.groupes)
        sections.append(f"### Groupes\n{lines}")
    if results.dossiers:
        lines = "\n".join(
            f"- {truncate(hit.titre, 180)}"
            + (f" ({hit.procedure_label})" if hit.procedure_label else "")
            for hit in results.dossiers
        )
        sections.append(f"### Dossiers législatifs\n{lines}")
    if not sections:
        body = (
            f"Aucun résultat pour « {query} ». Essayez des mots-clés plus courts, "
            "avec les accents français."
        )
        return finish(body, response_source_line(response))
    note = (
        f"_{response.attributes.total} résultat(s) au total ; 8 au plus par catégorie. "
        "Pour en voir davantage, utilisez `rechercher_scrutins` ou `rechercher_deputes`._"
    )
    body = f"## Résultats pour « {query} »\n\n" + "\n\n".join(sections) + f"\n\n{note}"
    return finish(body, response_source_line(response))


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


def position_from_votes(response: CivixResponse[ScrutinVotes], depute_uid: str) -> ScrutinPosition:
    """Retrouve le vote d'un député dans les votes d'un scrutin."""
    scrutin = response.attributes.scrutin
    vote = next((v for v in response.attributes.votes if v.deputy_uid == depute_uid), None)
    return ScrutinPosition(
        uid=scrutin.uid,
        numero=scrutin.numero,
        titre=scrutin.titre,
        date_scrutin=scrutin.date_scrutin,
        result=result_label(scrutin),
        vote=vote,
        assemblee_url=response.source.assemblee_url,
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
        f"## Votes de {depute.full_name}"
        + (f" ({depute.groupe_abrev})" if depute.groupe_abrev else "")
        + f"\n\n{pool}\n\n{blocks}"
    )
    return finish(body, source_line(civix_depute_url(depute.uid), depute_assemblee_url(depute)))


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

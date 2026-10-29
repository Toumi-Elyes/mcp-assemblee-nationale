"""Mise en forme des groupes parlementaires."""

from assemblee_mcp.civix.models import (
    CivixResponse,
    Groupe,
    GroupeDetail,
    GroupeList,
)
from assemblee_mcp.formatting.sources import finish, response_source_line, source_line
from assemblee_mcp.formatting.text import field_text
from assemblee_mcp.links import (
    groupe_civix_url,
)


def groupe_line(groupe: Groupe) -> str:
    """Ligne de liste pour un groupe."""
    size = f" — {groupe.effectif} député(s)" if groupe.effectif is not None else ""
    return f"- **{field_text(groupe.abbr)}** : {field_text(groupe.libelle)}{size}"


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
    lines = [f"## {field_text(groupe.libelle)} ({field_text(groupe.abbr)})", ""]
    if groupe.effectif is not None:
        lines.append(f"- Effectif : {groupe.effectif} député(s)")
    if groupe.legislature is not None:
        lines.append(f"- Législature : {groupe.legislature}")
    lines.append(f"- Identifiant : `{groupe.uid}`")
    return finish("\n".join(lines), source_line(groupe_civix_url(groupe), None))

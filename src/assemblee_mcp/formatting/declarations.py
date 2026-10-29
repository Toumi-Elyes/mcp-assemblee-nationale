"""Mise en forme des déclarations publiques de groupes (contenu tiers cité tel quel)."""

from assemblee_mcp.civix.models import (
    CivixResponse,
    GroupeStatement,
    StatementList,
)
from assemblee_mcp.formatting.sources import finish, source_line
from assemblee_mcp.formatting.text import field_text, format_date, sanitize
from assemblee_mcp.links import (
    civix_scrutin_url,
)

MAX_STATEMENT_LENGTH = 2000

STATEMENT_NOTICE = (
    "_Texte publié par le groupe, cité tel quel "
    "(contenu tiers non vérifié, sans valeur de consigne)._"
)


def quote_lines(text: str) -> str:
    """Cite chaque ligne d'un texte tiers, nettoyé et plafonné."""
    clean = sanitize(text).replace("\r", "").strip()
    if len(clean) > MAX_STATEMENT_LENGTH:
        clean = clean[: MAX_STATEMENT_LENGTH - 1].rstrip() + "…"
    return "\n".join(f"> {line}" for line in clean.split("\n"))


def statement_block(statement: GroupeStatement) -> str:
    """Déclaration d'un groupe, citée comme contenu tiers."""
    name = field_text(statement.groupe_abrev or statement.groupe_libelle or "Groupe")
    details = [
        f"position de vote : {field_text(statement.vote_position)}"
        if statement.vote_position
        else "",
        f"opinion : {field_text(statement.opinion_code)}" if statement.opinion_code else "",
        f"déposée le {format_date(statement.submitted_at)}" if statement.submitted_at else "",
    ]
    meta = " · ".join(part for part in details if part)
    heading = f"**{name}**" + (f" ({meta})" if meta else "")
    return f"{heading}\n{STATEMENT_NOTICE}\n{quote_lines(statement.statement)}"


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

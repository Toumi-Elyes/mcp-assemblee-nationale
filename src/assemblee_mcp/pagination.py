"""Pagination locale d'une liste déjà entièrement en mémoire."""

from collections.abc import Sequence

from assemblee_mcp.civix.models import Pagination


def paginate[Item](
    items: Sequence[Item], page: int, page_size: int
) -> tuple[list[Item], Pagination]:
    """Page `page` (à partir de 1) d'une liste, avec la pagination au format CIVIX."""
    start = (page - 1) * page_size
    end = start + page_size
    pagination = Pagination(
        page=page,
        page_size=page_size,
        next_page=page + 1 if end < len(items) else None,
        count_total=len(items),
    )
    return list(items[start:end]), pagination

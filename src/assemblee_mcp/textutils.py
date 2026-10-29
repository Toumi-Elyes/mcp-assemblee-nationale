"""Utilitaires de texte : comparaison insensible aux accents et à la casse."""

import unicodedata


def fold(text: str) -> str:
    """Minuscules sans accents, pour comparer des noms."""
    decomposed = unicodedata.normalize("NFKD", text)
    stripped = "".join(char for char in decomposed if not unicodedata.combining(char))
    return stripped.casefold().replace("-", " ").replace("'", " ").replace("’", " ")


def tokens(text: str) -> list[str]:
    """Mots normalisés d'un texte."""
    return fold(text).split()

"""Erreurs de l'API CIVIX, avec des messages en français destinés à l'utilisateur."""

UNAVAILABLE_MESSAGE = (
    "Le service CIVIX est momentanément indisponible. Réessayez dans quelques instants."
)
NOT_FOUND_MESSAGE = "Aucune donnée trouvée sur CIVIX pour cette demande (identifiant inconnu ?)."
UNEXPECTED_MESSAGE = "CIVIX a renvoyé une réponse inattendue. Réessayez plus tard."


class CivixError(Exception):
    """Erreur générique : le message est sûr à montrer à un utilisateur non technique."""

    def __init__(self, message: str = UNAVAILABLE_MESSAGE) -> None:
        """Mémorise le message français destiné à l'utilisateur."""
        super().__init__(message)
        self.message = message


class CivixNotFoundError(CivixError):
    """La ressource demandée n'existe pas (HTTP 404)."""

    def __init__(self, message: str = NOT_FOUND_MESSAGE) -> None:
        """Construit l'erreur « introuvable », avec un message personnalisable."""
        super().__init__(message)


class CivixUnavailableError(CivixError):
    """Le service est injoignable ou en erreur après nouvelle tentative."""

    def __init__(self, message: str = UNAVAILABLE_MESSAGE) -> None:
        """Construit l'erreur « service indisponible »."""
        super().__init__(message)

"""Budget d'appels réseau par appel d'outil, partagé entre les tâches lancées en parallèle."""

from collections.abc import Iterator
from contextlib import contextmanager
from contextvars import ContextVar

from assemblee_mcp.civix.errors import CivixError
from assemblee_mcp.limits import DEFAULT_MAX_CALLS

TOO_BROAD_MESSAGE = "Demande trop large : précisez le nom, le groupe ou le sujet."


class CivixBudgetError(CivixError):
    """Le nombre d'appels autorisés pour cette demande est épuisé."""

    def __init__(self) -> None:
        """Construit l'erreur avec le message « demande trop large »."""
        super().__init__(TOO_BROAD_MESSAGE)


class CallBudget:
    """Compteur d'appels réseau ; les succès de cache ne sont pas comptés."""

    def __init__(self, max_calls: int = DEFAULT_MAX_CALLS) -> None:
        """Crée un budget de `max_calls` appels, aucun n'étant encore consommé."""
        self.max_calls = max_calls
        self.used = 0

    @property
    def remaining(self) -> int:
        """Nombre d'appels encore autorisés."""
        return self.max_calls - self.used

    def charge(self) -> None:
        """Compte un appel réseau ; lève `CivixBudgetError` si le budget est épuisé."""
        if self.used >= self.max_calls:
            raise CivixBudgetError
        self.used += 1


current_budget: ContextVar[CallBudget | None] = ContextVar("civix_call_budget", default=None)


def charge_call() -> None:
    """Compte un appel dans le budget courant, s'il y en a un."""
    budget = current_budget.get()
    if budget is not None:
        budget.charge()


def can_afford(calls: int) -> bool:
    """Vrai si le budget courant permet encore `calls` appels (toujours vrai sans budget)."""
    budget = current_budget.get()
    return budget is None or budget.remaining >= calls


@contextmanager
def unbudgeted() -> Iterator[None]:
    """Suspend le budget pour un chargement mis en cache longtemps (annuaire des députés)."""
    token = current_budget.set(None)
    try:
        yield
    finally:
        current_budget.reset(token)

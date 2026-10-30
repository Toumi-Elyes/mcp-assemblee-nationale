"""Faux stockage partagé en mémoire, pour tester le second niveau de cache sans Vercel."""

import asyncio
from collections.abc import Sequence
from dataclasses import dataclass, field
from typing import Any


@dataclass
class StoredEntry:
    value: Any
    ttl: int
    tags: tuple[str, ...]


@dataclass
class FakeBackend:
    """Stockage clé-valeur qui garde ce qu'on lui donne et compte ses accès."""

    entries: dict[str, StoredEntry] = field(default_factory=dict)
    reads: int = 0
    writes: int = 0

    async def get(self, key: str) -> object | None:
        self.reads += 1
        entry = self.entries.get(key)
        return None if entry is None else entry.value

    async def set(self, key: str, value: object, ttl: int, tags: Sequence[str]) -> None:
        self.writes += 1
        self.entries[key] = StoredEntry(value, ttl, tuple(tags))


class BrokenBackend(FakeBackend):
    """Stockage en panne : chaque accès lève une erreur."""

    async def get(self, key: str) -> object | None:
        self.reads += 1
        raise ConnectionError

    async def set(self, key: str, value: object, ttl: int, tags: Sequence[str]) -> None:
        self.writes += 1
        raise ConnectionError


class HangingBackend(FakeBackend):
    """Stockage qui ne répond jamais."""

    async def get(self, key: str) -> object | None:
        self.reads += 1
        await asyncio.sleep(3600)
        return None

    async def set(self, key: str, value: object, ttl: int, tags: Sequence[str]) -> None:
        self.writes += 1
        await asyncio.sleep(3600)

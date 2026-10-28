"""The event log: an ordered record of what happened in each run.

Every write has an operation key. Writing the same (run_id, op_key) twice is ignored,
so a step that runs again after a crash or a repeated command never logs twice.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any


class EventLog(ABC):
    @abstractmethod
    def record(self, run_id: str, op_key: str, event: str, **details: Any) -> bool:
        """Store one event. Return False if this (run_id, op_key) was already stored."""

    @abstractmethod
    def events(self, run_id: str) -> list[dict[str, Any]]:
        """Return the run's events in the order they were stored."""


class InMemoryEventLog(EventLog):
    """Event log for tests. It is lost when the process ends."""

    def __init__(self) -> None:
        self._rows: list[dict[str, Any]] = []
        self._keys: set[tuple[str, str]] = set()

    def record(self, run_id: str, op_key: str, event: str, **details: Any) -> bool:
        key = (run_id, op_key)
        if key in self._keys:
            return False
        self._keys.add(key)
        self._rows.append({"run_id": run_id, "event": event, **details})
        return True

    def events(self, run_id: str) -> list[dict[str, Any]]:
        return [
            {k: v for k, v in row.items() if k != "run_id"}
            for row in self._rows
            if row["run_id"] == run_id
        ]

from __future__ import annotations

import json
from pathlib import Path

from evoting.domain.state import SystemState


class StorageError(RuntimeError):
    """Raised when system data cannot be loaded or saved."""


class JsonStorageRepository:
    def __init__(self, data_file: Path) -> None:
        self.data_file = data_file

    def load(self) -> SystemState:
        if not self.data_file.exists():
            return SystemState()

        try:
            with self.data_file.open("r", encoding="utf-8") as handle:
                payload = json.load(handle)
        except json.JSONDecodeError as error:
            raise StorageError(f"Corrupted data file: {error}") from error
        except OSError as error:
            raise StorageError(f"File system error while loading data: {error}") from error

        if not isinstance(payload, dict):
            raise StorageError("Invalid data file structure.")
        return SystemState.from_dict(payload)

    def save(self, state: SystemState) -> None:
        try:
            with self.data_file.open("w", encoding="utf-8") as handle:
                json.dump(state.serialize(), handle, indent=2)
        except OSError as error:
            raise StorageError(f"File system error while saving data: {error}") from error

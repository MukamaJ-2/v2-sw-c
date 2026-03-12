from __future__ import annotations

from collections.abc import Callable
from typing import TYPE_CHECKING
from typing import Any

from evoting.domain.state import SystemState
from evoting.repository.storage import JsonStorageRepository, StorageError
from evoting.ui.console import Console

if TYPE_CHECKING:
    from evoting.services.audit_service import AuditService


class BaseService:
    def __init__(
        self,
        state: SystemState,
        console: Console,
        storage: JsonStorageRepository,
        audit: AuditService | None = None,
    ) -> None:
        self.state = state
        self.console = console
        self.storage = storage
        self.audit = audit

    def show_screen(self, title: str, theme_color: str) -> None:
        self.console.clear_screen()
        self.console.header(title, theme_color)

    def stop(self, message: str, level: str = "error") -> None:
        getattr(self.console, level)(message)
        self.console.pause()

    def require_records(self, records: dict[Any, Any], empty_message: str) -> bool:
        if records:
            return True
        print()
        self.console.info(empty_message)
        self.console.pause()
        return False

    def select_record(
        self,
        records: dict[int, dict],
        render_record: Callable[[dict], str],
        prompt_text: str,
        not_found_message: str,
        *,
        invalid_message: str = "Invalid input.",
    ) -> tuple[int | None, dict | None]:
        print()
        for record in records.values():
            print(render_record(record))
        try:
            record_id = int(self.console.prompt(prompt_text))
        except ValueError:
            self.stop(invalid_message)
            return None, None
        record = records.get(record_id)
        if record is None:
            self.stop(not_found_message)
            return None, None
        return record_id, record

    def confirm(self, prompt_text: str) -> bool:
        return self.console.prompt(prompt_text).strip().lower() == "yes"

    def persist(self) -> bool:
        try:
            self.storage.save(self.state)
        except StorageError as error:
            self.console.error(str(error))
            return False
        self.console.info("Data saved successfully")
        return True

from __future__ import annotations

from evoting.domain.state import SystemState, timestamp_now


class AuditService:
    def __init__(self, state: SystemState) -> None:
        self.state = state

    def log(self, action: str, user: str, details: str) -> None:
        self.state.audit_log.append(
            {
                "timestamp": timestamp_now(),
                "action": action,
                "user": user,
                "details": details,
            }
        )

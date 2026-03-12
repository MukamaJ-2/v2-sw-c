from __future__ import annotations

MIN_CANDIDATE_AGE = 25
MAX_CANDIDATE_AGE = 75
MIN_VOTER_AGE = 18
MIN_PASSWORD_LENGTH = 6
VOTER_CARD_LENGTH = 12

REQUIRED_EDUCATION_LEVELS = [
    "Bachelor's Degree",
    "Master's Degree",
    "PhD",
    "Doctorate",
]

VALID_GENDERS = {"M", "F", "OTHER"}
VALID_POSITION_LEVELS = {"national", "regional", "local"}
DEFAULT_ADMIN_USERNAME = "admin"
DEFAULT_ADMIN_PASSWORD = "admin123"
DEFAULT_ADMIN_EMAIL = "admin@evote.com"
DEFAULT_ADMIN_FULL_NAME = "System Administrator"
DEFAULT_ADMIN_ROLE = "super_admin"

ROLE_MAP = {
    "1": "super_admin",
    "2": "election_officer",
    "3": "station_manager",
    "4": "auditor",
}

POLL_STATUS_DRAFT = "draft"
POLL_STATUS_OPEN = "open"
POLL_STATUS_CLOSED = "closed"

MIN_CANDIDATE_AGE = 25
MAX_CANDIDATE_AGE = 75
REQUIRED_EDUCATION_LEVELS = [
    "Bachelor's Degree", "Master's Degree", "PhD", "Doctorate"
]
MIN_VOTER_AGE = 18
MIN_PASSWORD_LENGTH = 6

VALID_GENDERS = ["M", "F", "OTHER"]
VALID_POSITION_LEVELS = ["national", "regional", "local"]

DATA_FILE_PATH = "evoting_data.json"
VOTER_CARD_LENGTH = 12
VOTE_HASH_LENGTH = 16

AUDIT_LOG_DEFAULT_LIMIT = 20
BAR_CHART_WIDTH = 50

TURNOUT_HIGH_THRESHOLD = 50
TURNOUT_MEDIUM_THRESHOLD = 25
STATION_LOAD_WARNING_PERCENT = 75
STATION_LOAD_CRITICAL_PERCENT = 100

ADMIN_ROLES = {
    "1": "super_admin",
    "2": "election_officer",
    "3": "station_manager",
    "4": "auditor",
}

ADMIN_ROLE_DESCRIPTIONS = {
    "super_admin": "Full access",
    "election_officer": "Manage polls and candidates",
    "station_manager": "Manage stations and verify voters",
    "auditor": "Read-only access",
}

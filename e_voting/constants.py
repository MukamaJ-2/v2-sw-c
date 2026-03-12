"""
Application-wide constants for the National E-Voting System.

All magic numbers and magic strings from the original monolith are
extracted here so they can be changed in one place (DRY principle).
Grouped by domain area for readability.
"""

# ── Candidate Eligibility Rules ──────────────────────────────
# Candidates must fall within this age range to stand for election
MIN_CANDIDATE_AGE = 25
MAX_CANDIDATE_AGE = 75

# Only candidates with these education levels are accepted
REQUIRED_EDUCATION_LEVELS = [
    "Bachelor's Degree", "Master's Degree", "PhD", "Doctorate"
]

# ── Voter Eligibility Rules ──────────────────────────────────
MIN_VOTER_AGE = 18
MIN_PASSWORD_LENGTH = 6

# ── Validation Sets ──────────────────────────────────────────
VALID_GENDERS = ["M", "F", "OTHER"]
VALID_POSITION_LEVELS = ["national", "regional", "local"]

# ── Persistence & Security ───────────────────────────────────
DATA_FILE_PATH = "evoting_data.json"
VOTER_CARD_LENGTH = 12       # Random alphanumeric voter card ID length
VOTE_HASH_LENGTH = 16        # Truncated SHA-256 hash shown as vote receipt

# ── Display / Reporting ──────────────────────────────────────
AUDIT_LOG_DEFAULT_LIMIT = 20
BAR_CHART_WIDTH = 50         # Max characters for the result bar chart

# Turnout percentage thresholds for color-coding in reports
TURNOUT_HIGH_THRESHOLD = 50
TURNOUT_MEDIUM_THRESHOLD = 25

# Station capacity utilisation thresholds (percentage)
STATION_LOAD_WARNING_PERCENT = 75
STATION_LOAD_CRITICAL_PERCENT = 100

# ── Admin Role Definitions ───────────────────────────────────
# Maps menu choice number to internal role name
ADMIN_ROLES = {
    "1": "super_admin",
    "2": "election_officer",
    "3": "station_manager",
    "4": "auditor",
}

# Human-readable descriptions shown in the admin creation menu
ADMIN_ROLE_DESCRIPTIONS = {
    "super_admin": "Full access",
    "election_officer": "Manage polls and candidates",
    "station_manager": "Manage stations and verify voters",
    "auditor": "Read-only access",
}

from pathlib import Path


# Project root
BASE_DIR = Path(__file__).resolve().parent.parent

# Data directories
DATA_DIR = BASE_DIR / "data"
KNOWLEDGE_BASE_DIR = BASE_DIR / "knowledge_base"
VECTOR_STORE_DIR = BASE_DIR / "vector_store"
OUTPUT_DIR = BASE_DIR / "outputs"

# Input files
EMPLOYEE_REQUESTS_FILE = DATA_DIR / "employee_requests.json"
TICKETS_FILE = DATA_DIR / "tickets.json"

# Output directories
PROCESSED_REQUESTS_DIR = OUTPUT_DIR / "processed_requests"
GENERATED_TICKETS_DIR = OUTPUT_DIR / "generated_tickets"
AUDIT_LOGS_DIR = OUTPUT_DIR / "audit_logs"


def create_directories():
    """Create required runtime directories."""

    PROCESSED_REQUESTS_DIR.mkdir(parents=True, exist_ok=True)
    GENERATED_TICKETS_DIR.mkdir(parents=True, exist_ok=True)
    AUDIT_LOGS_DIR.mkdir(parents=True, exist_ok=True)
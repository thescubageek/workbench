import os

DEFAULT_TIMEOUT_SECONDS = 10
MAX_RETRIES = 3
BROKEN_STATUS_MIN = 400


def timeout_seconds():
    return float(os.environ.get("LINKCHECK_TIMEOUT", DEFAULT_TIMEOUT_SECONDS))

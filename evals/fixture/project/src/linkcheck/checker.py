import urllib.error
import urllib.request

from linkcheck.config import BROKEN_STATUS_MIN, MAX_RETRIES, timeout_seconds


class LinkCheckError(Exception):
    pass


def fetch_status(url, timeout):
    request = urllib.request.Request(url, method="HEAD")
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            return response.status
    except urllib.error.HTTPError as error:
        return error.code


def is_broken(status):
    return status >= BROKEN_STATUS_MIN


def check_url(url):
    last_error = None
    for _ in range(MAX_RETRIES):
        try:
            return not is_broken(fetch_status(url, timeout_seconds()))
        except (urllib.error.URLError, TimeoutError) as error:
            last_error = error
    raise LinkCheckError(f"{url}: gave up after {MAX_RETRIES} attempts: {last_error}")

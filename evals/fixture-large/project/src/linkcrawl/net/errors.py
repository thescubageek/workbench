"""Transport-level failures. An HTTP error status is not one of these."""


class NetworkError(Exception):
    """A request did not produce an HTTP status."""

    retryable = True
    kind = "network"

    def __init__(self, url, message):
        super().__init__(f"{url}: {message}")
        self.url = url
        self.message = message


class TimeoutExceeded(NetworkError):
    kind = "timeout"


class ConnectionFailed(NetworkError):
    kind = "connection"


class DnsFailure(NetworkError):
    """The host name did not resolve; retrying rarely helps."""

    retryable = False
    kind = "dns"


class TooManyRedirects(NetworkError):
    retryable = False
    kind = "redirects"


class InvalidUrl(NetworkError):
    retryable = False
    kind = "invalid-url"

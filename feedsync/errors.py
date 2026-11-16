"""Errors a fetch can end with."""


class FetchError(Exception):
    """A request failed after every retry."""

    def __init__(self, url, status=None, reason=""):
        super().__init__(f"{url}: {status or 'no response'} {reason}".strip())
        self.url = url
        self.status = status
        self.reason = reason


class AuthError(FetchError):
    """The source refused the credentials (401 or 403). Never retried."""


class ParseError(Exception):
    """The body was fetched but is not the format the source declares."""

    def __init__(self, url, detail):
        super().__init__(f"{url}: {detail}")
        self.url = url
        self.detail = detail

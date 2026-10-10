"""Synthetic disposable file for the BPR-1222 two-account tour course."""


def parse_header(line):
    """Split a 'key: value' header line."""
    if ":" not in line:
        raise ValueError("header without a colon")
    key, value = line.split(":", 1)
    return key.strip().lower(), value.strip()


def parse_headers(lines):
    """Collect headers until the first blank line."""
    headers = {}
    for line in lines:
        if not line.strip():
            break
        key, value = parse_header(line)
        headers.setdefault(key, []).append(value)
    return headers


def content_length(headers):
    """Return the declared body length, or zero."""
    values = headers.get("content-length", ["0"])
    if len(values) != 1:
        raise ValueError("conflicting content-length headers")
    length = int(values[0])
    if length < 0:
        raise ValueError("negative content-length")
    return length

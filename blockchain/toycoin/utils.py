"""Utility functions.
"""


import datetime # type: ignore
import pytz # type: ignore


################################################################################
# Bytes


def int_to_bytes(n: int) -> bytes:
    """Convert int to bytes."""
    return bytes(str(n).encode('utf-8'))


################################################################################
# Time


def timestamp() -> int:
    """Epoch now (UTC seconds)."""
    return int(datetime.datetime.now(pytz.utc).timestamp())


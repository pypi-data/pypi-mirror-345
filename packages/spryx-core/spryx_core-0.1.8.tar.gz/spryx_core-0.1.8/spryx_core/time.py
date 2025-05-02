"""
Time and date utilities.

This module provides functions for working with dates and times in UTC,
including ISO-8601 formatting, parsing, and common time operations.
"""

from __future__ import annotations

import re
from datetime import datetime, timedelta, timezone

# Regular expression for validating ISO-8601 UTC timestamps
ISO_8601_UTC_RE = re.compile(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d+)?Z$")


def now_utc() -> datetime:
    """
    Get the current UTC datetime.

    Returns:
        datetime: The current time in UTC timezone
    """
    return datetime.now(timezone.utc)


def to_iso(dt: datetime, *, milliseconds: bool = False) -> str:
    """
    Convert a datetime to ISO-8601 format with Z suffix (UTC).

    Args:
        dt: The datetime to convert
        milliseconds: If True, include milliseconds; otherwise, include microseconds

    Returns:
        str: ISO-8601 formatted string in UTC
    """
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    dt = dt.astimezone(timezone.utc)

    if milliseconds:
        frac = f"{dt.microsecond // 1000:03d}"
        return dt.strftime(f"%Y-%m-%dT%H:%M:%S.{frac}Z")
    return dt.strftime("%Y-%m-%dT%H:%M:%S.%fZ")


def parse_iso(value: str) -> datetime:
    """
    Parse an ISO-8601 UTC string into a datetime.

    Args:
        value: ISO-8601 string with Z suffix

    Returns:
        datetime: Parsed datetime with UTC timezone

    Raises:
        ValueError: If the string is not in valid ISO-8601 UTC format
    """
    if not ISO_8601_UTC_RE.fullmatch(value):
        raise ValueError("Formato ISO inválido")
    return datetime.fromisoformat(value.replace("Z", "+00:00")).astimezone(timezone.utc)


def utc_from_timestamp(ts: int | float) -> datetime:
    """
    Convert a UNIX timestamp to a UTC datetime.

    Args:
        ts: UNIX timestamp (seconds since epoch)

    Returns:
        datetime: Corresponding datetime in UTC timezone
    """
    return datetime.fromtimestamp(ts, tz=timezone.utc)


def start_of_day(dt: datetime | None = None) -> datetime:
    """
    Get the start of day (00:00:00.000000) for a given datetime.

    Args:
        dt: Input datetime (defaults to current UTC time if None)

    Returns:
        datetime: Start of day (midnight) in UTC timezone
    """
    dt = dt or now_utc()
    return dt.replace(hour=0, minute=0, second=0, microsecond=0, tzinfo=timezone.utc)


def end_of_day(dt: datetime | None = None) -> datetime:
    """
    Get the end of day (23:59:59.999999) for a given datetime.

    Args:
        dt: Input datetime (defaults to current UTC time if None)

    Returns:
        datetime: End of day (1 microsecond before midnight) in UTC timezone
    """
    return start_of_day(dt) + timedelta(days=1, microseconds=-1)

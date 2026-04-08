from __future__ import annotations
import csv
import io
import uuid
from typing import Any, BinaryIO

REQUIRED_COLUMNS = {"user_id", "timestamp", "resource", "action", "success"}
OPTIONAL_COLUMNS = {
    "event_id", "ip_address", "latitude", "longitude", "location",
    "user_agent", "device_id", "mfa_used", "failure_reason", "privilege_level",
}
ALL_COLUMNS = REQUIRED_COLUMNS | OPTIONAL_COLUMNS

_BOOL_TRUE = {"1", "true", "yes"}
_BOOL_FALSE = {"0", "false", "no", ""}


def _coerce_bool(val: str | None) -> bool | None:
    if val is None:
        return None
    v = str(val).strip().lower()
    if v in _BOOL_TRUE:
        return True
    if v in _BOOL_FALSE:
        return False
    return None


def _coerce_float(val: str | None) -> float | None:
    if val is None or str(val).strip() == "":
        return None
    try:
        return float(val)
    except ValueError:
        return None


def parse_csv(file: BinaryIO | io.TextIOBase) -> tuple[list[dict[str, Any]], list[str]]:
    """Parse a CSV file into a list of event dicts.

    Returns (rows, errors) where errors is a list of human-readable messages.
    """
    errors: list[str] = []
    rows: list[dict[str, Any]] = []

    text: io.TextIOBase
    if isinstance(file, io.TextIOBase):
        text = file
    else:
        text = io.TextIOWrapper(file, encoding="utf-8-sig")

    reader = csv.DictReader(text)
    if reader.fieldnames is None:
        errors.append("CSV file is empty or has no header row.")
        return rows, errors

    header_set = set(reader.fieldnames)
    missing = REQUIRED_COLUMNS - header_set
    if missing:
        errors.append(f"Missing required columns: {', '.join(sorted(missing))}")
        return rows, errors

    for i, raw in enumerate(reader, start=2):
        row_errors: list[str] = []
        for col in REQUIRED_COLUMNS:
            if not raw.get(col, "").strip():
                row_errors.append(f"row {i}: missing value for '{col}'")
        if row_errors:
            errors.extend(row_errors)
            continue

        event: dict[str, Any] = {
            "event_id": raw.get("event_id", "").strip() or str(uuid.uuid4()),
            "user_id": raw["user_id"].strip(),
            "timestamp": raw["timestamp"].strip(),
            "resource": raw["resource"].strip(),
            "action": raw["action"].strip(),
            "success": _coerce_bool(raw["success"]) or False,
            "ip_address": raw.get("ip_address", "").strip() or None,
            "latitude": _coerce_float(raw.get("latitude")),
            "longitude": _coerce_float(raw.get("longitude")),
            "location": raw.get("location", "").strip() or None,
            "user_agent": raw.get("user_agent", "").strip() or None,
            "device_id": raw.get("device_id", "").strip() or None,
            "mfa_used": _coerce_bool(raw.get("mfa_used")),
            "failure_reason": raw.get("failure_reason", "").strip() or None,
            "privilege_level": raw.get("privilege_level", "").strip() or None,
        }
        rows.append(event)

    return rows, errors

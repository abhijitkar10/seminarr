from __future__ import annotations
import csv
import io
import uuid
import hashlib
from typing import Any, BinaryIO
from pathlib import Path
import pandas as pd

REQUIRED_COLUMNS = {"user_id", "timestamp", "resource", "action", "success"}
OPTIONAL_COLUMNS = {
    "event_id", "ip_address", "latitude", "longitude", "location",
    "user_agent", "device_id", "mfa_used", "failure_reason", "privilege_level",
}
ALL_COLUMNS = REQUIRED_COLUMNS | OPTIONAL_COLUMNS


def _generate_deterministic_event_id(user_id: str, timestamp: str, resource: str, action: str) -> str:
    """Generate a deterministic event_id from event attributes.
    
    This ensures the same event gets the same ID when loaded multiple times,
    preventing duplicates when the same source file is re-ingested.
    """
    key = f"{user_id}|{timestamp}|{resource}|{action}".encode('utf-8')
    hash_digest = hashlib.sha256(key).hexdigest()[:16]
    return hash_digest

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
            "event_id": raw.get("event_id", "").strip() or _generate_deterministic_event_id(
                raw["user_id"].strip(),
                raw["timestamp"].strip(),
                raw["resource"].strip(),
                raw["action"].strip()
            ),
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


def parse_excel(file_path: str | Path) -> tuple[list[dict[str, Any]], list[str]]:
    """Parse an Excel file (.xlsx) into a list of event dicts.
    
    Automatically maps common column name variations to standard names.
    Auto-generates 'action' and 'resource' if not present.
    
    Args:
        file_path: Path to .xlsx file
    
    Returns:
        (rows, errors) where errors is a list of human-readable messages.
    """
    errors: list[str] = []
    rows: list[dict[str, Any]] = []
    
    file_path = Path(file_path)
    if not file_path.exists():
        errors.append(f"File not found: {file_path}")
        return rows, errors
    
    try:
        df = pd.read_excel(file_path)
    except Exception as e:
        errors.append(f"Failed to read Excel file: {str(e)}")
        return rows, errors
    
    # Column name mapping for common variations
    column_mapping = {
        # Timestamp variations
        'login timestamp': 'timestamp',
        'timestamp': 'timestamp',
        'date': 'timestamp',
        'time': 'timestamp',
        
        # User ID variations
        'user id': 'user_id',
        'user_id': 'user_id',
        'userid': 'user_id',
        'username': 'user_id',
        
        # Success variations
        'login successful': 'success',
        'success': 'success',
        'is_successful': 'success',
        'successful': 'success',
        
        # IP Address variations
        'ip address': 'ip_address',
        'ip_address': 'ip_address',
        'ipaddress': 'ip_address',
        'ip': 'ip_address',
        
        # Other optional columns
        'country': 'country',
        'region': 'region',
        'city': 'city',
        'asn': 'asn',
        'user agent string': 'user_agent',
        'user_agent': 'user_agent',
        'browser name and version': 'browser',
        'os name and version': 'os',
        'device type': 'device_type',
        'device_id': 'device_id',
        'is attack ip': 'is_attack',
        'is account takeover': 'is_account_takeover',
        'round-trip time [ms]': 'rtt_ms',
    }
    
    # Normalize and map column names
    normalized_df = df.copy()
    column_remap = {}
    for col in normalized_df.columns:
        col_lower = col.strip().lower()
        if col_lower in column_mapping:
            new_col = column_mapping[col_lower]
            if new_col not in column_remap.values():  # Avoid duplicates
                column_remap[col] = new_col
    
    normalized_df = normalized_df.rename(columns=column_remap)
    
    # Auto-generate missing required columns
    if 'resource' not in normalized_df.columns:
        normalized_df['resource'] = 'Authentication'
    if 'action' not in normalized_df.columns:
        normalized_df['action'] = 'LOGIN'
    
    # Check for required columns after mapping and auto-generation
    missing = REQUIRED_COLUMNS - set(normalized_df.columns)
    if missing:
        errors.append(f"Missing required columns: {', '.join(sorted(missing))}")
        return rows, errors
    
    # Parse each row
    for i, (idx, raw) in enumerate(normalized_df.iterrows(), start=2):
        row_errors: list[str] = []
        
        # Check for missing required values
        for col in REQUIRED_COLUMNS:
            val = raw.get(col, "")
            if pd.isna(val) or (isinstance(val, str) and str(val).strip() == ""):
                row_errors.append(f"row {i}: missing value for '{col}'")
        
        if row_errors:
            errors.extend(row_errors)
            continue
        
        # Convert timestamp to ISO format if needed
        ts = raw["timestamp"]
        if pd.api.types.is_datetime64_any_dtype(type(ts)):
            ts_str = ts.isoformat()
        else:
            ts_str = str(ts).strip()
        
        event: dict[str, Any] = {
            "event_id": (str(raw.get("event_id", "")).strip() if not pd.isna(raw.get("event_id")) and str(raw.get("event_id", "")).strip() else None) or _generate_deterministic_event_id(
                str(raw["user_id"]).strip(),
                ts_str,
                str(raw["resource"]).strip() if not pd.isna(raw.get("resource")) else "Authentication",
                str(raw["action"]).strip() if not pd.isna(raw.get("action")) else "LOGIN"
            ),
            "user_id": str(raw["user_id"]).strip(),
            "timestamp": ts_str,
            "resource": str(raw["resource"]).strip() if not pd.isna(raw.get("resource")) else "Authentication",
            "action": str(raw["action"]).strip() if not pd.isna(raw.get("action")) else "LOGIN",
            "success": _coerce_bool(str(raw["success"])) or False,
            "ip_address": str(raw.get("ip_address", "")).strip() if not pd.isna(raw.get("ip_address")) else None,
            "latitude": _coerce_float(str(raw.get("latitude"))) if not pd.isna(raw.get("latitude")) else None,
            "longitude": _coerce_float(str(raw.get("longitude"))) if not pd.isna(raw.get("longitude")) else None,
            "location": str(raw.get("location", f"{raw.get('country', '')}-{raw.get('city', '')}")).strip() if not pd.isna(raw.get("location")) else None,
            "user_agent": str(raw.get("user_agent", "")).strip() if not pd.isna(raw.get("user_agent")) else None,
            "device_id": str(raw.get("device_id", "")).strip() if not pd.isna(raw.get("device_id")) else None,
            "mfa_used": _coerce_bool(str(raw.get("mfa_used"))) if not pd.isna(raw.get("mfa_used")) else None,
            "failure_reason": str(raw.get("failure_reason", "")).strip() if not pd.isna(raw.get("failure_reason")) else None,
            "privilege_level": str(raw.get("privilege_level", "")).strip() if not pd.isna(raw.get("privilege_level")) else None,
        }
        rows.append(event)
    
    return rows, errors


def load_book1() -> tuple[list[dict[str, Any]], list[str]]:
    """Load and parse Book1.xlsx from project root."""
    book1_path = Path(__file__).resolve().parent.parent / "Book1.xlsx"
    return parse_excel(book1_path)


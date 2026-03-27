from __future__ import annotations
from typing import Dict, Any
from datetime import datetime
from uuid import uuid4
import json
import os
import smtplib
from email.message import EmailMessage
from data.db import insert_alert


def maybe_send_alert(event_id: str, user_id: str, risk: float, reasons: list, contributions: dict, threshold: float = 1.5) -> Dict[str, Any]:
    payload = {
        "event_id": event_id,
        "user_id": user_id,
        "risk": risk,
        "reasons": reasons,
        "contributions": contributions,
    }
    alert_meta = {}
    if risk >= threshold:
        alert_id = str(uuid4())
        now = datetime.utcnow().isoformat()
        channel = "console"
        # console "notification"
        print(f"[ALERT] user={user_id} event={event_id} risk={risk:.2f} reasons={reasons}")
        insert_alert(alert_id, event_id, user_id, risk, now, channel, json.dumps(payload))
        alert_meta = {"alert_id": alert_id, "channel": channel}
        # optional email
        email_to = os.getenv("ALERT_EMAIL_TO")
        email_from = os.getenv("ALERT_EMAIL_FROM")
        smtp_host = os.getenv("SMTP_HOST")
        if email_to and email_from and smtp_host:
            try:
                msg = EmailMessage()
                msg["Subject"] = f"[Anomaly Alert] user={user_id} risk={risk:.2f}"
                msg["From"] = email_from
                msg["To"] = email_to
                msg.set_content(json.dumps(payload, indent=2))
                with smtplib.SMTP(smtp_host) as s:
                    s.send_message(msg)
                channel = "email"
                insert_alert(alert_id, event_id, user_id, risk, now, channel, json.dumps(payload))
                alert_meta["channel"] = channel
            except Exception as e:
                print(f"[ALERT][EMAIL][ERROR] {e}")
    return alert_meta

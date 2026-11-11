from datetime import datetime, timedelta

from errors import Rejected
from sqlite_store import transaction

STATUSES = {"accepted", "in_transit", "out_for_delivery", "delivered"}


def operation(data, _):
    parcel, scans = data["parcel"], data["scans"]
    if not isinstance(parcel, str) or not parcel.strip() or not isinstance(scans, list):
        raise ValueError("Expected parcel and scans")
    with transaction() as db:
        db.execute("CREATE TABLE IF NOT EXISTS scan (parcel TEXT, id TEXT, at TEXT, status TEXT, PRIMARY KEY(parcel, id))")
        for scan in scans:
            event_id, at, status = scan["id"], datetime.fromisoformat(scan["at"]), scan["status"]
            if not isinstance(event_id, str) or not event_id.strip() or at.utcoffset() != timedelta(0) or status not in STATUSES:
                raise ValueError("Expected event ID, UTC timestamp and supported status")
            event = at.isoformat(timespec="microseconds"), status
            key = parcel, event_id
            previous = db.execute("SELECT at,status FROM scan WHERE parcel=? AND id=?", key).fetchone()
            if previous and previous != event:
                raise Rejected(409, "Scan ID already exists with different data")
            db.execute("INSERT OR IGNORE INTO scan VALUES (?, ?, ?, ?)", (*key, *event))
        rows = db.execute("SELECT id,at,status FROM scan WHERE parcel=? ORDER BY at,id", (parcel,)).fetchall()
    return {"history": [{"id": event_id, "at": at, "status": status} for event_id, at, status in rows]}

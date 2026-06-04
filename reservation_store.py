"""
Reservation store for the theatre final project.
In-memory by default; optional SQLite file (THEATRE_DB) shared by API and bot.
"""

from __future__ import annotations

import os
import sqlite3
import threading
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

import yaml

_lock = threading.Lock()


@dataclass
class BookingRecord:
    show_id: str
    customer_name: str
    seats: int
    zone: str
    accessibility: str
    confirmation_code: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


class ReservationStore:
    def __init__(
        self,
        shows_config: list[dict[str, Any]],
        db_path: Path | None = None,
    ):
        self._shows_config = list(shows_config)
        self._capacity: dict[str, int] = {
            s["id"]: int(s["capacity"]) for s in shows_config
        }
        self._used: dict[str, int] = {sid: 0 for sid in self._capacity}
        self._bookings: list[BookingRecord] = []
        self._counter = 0
        self._db_path = db_path
        if db_path:
            self._init_db()
            self._load_from_db()

    def _init_db(self) -> None:
        assert self._db_path
        self._db_path.parent.mkdir(parents=True, exist_ok=True)
        with sqlite3.connect(self._db_path) as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS bookings (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    show_id TEXT NOT NULL,
                    customer_name TEXT NOT NULL,
                    seats INTEGER NOT NULL,
                    zone TEXT NOT NULL,
                    accessibility TEXT NOT NULL,
                    confirmation_code TEXT NOT NULL UNIQUE
                )
                """
            )
            conn.commit()

    def _load_from_db(self) -> None:
        assert self._db_path
        with sqlite3.connect(self._db_path) as conn:
            rows = conn.execute(
                "SELECT show_id, customer_name, seats, zone, accessibility, confirmation_code "
                "FROM bookings ORDER BY id"
            ).fetchall()
        self._bookings = []
        self._used = {sid: 0 for sid in self._capacity}
        max_id = 0
        for show_id, customer_name, seats, zone, accessibility, code in rows:
            self._used[show_id] = self._used.get(show_id, 0) + int(seats)
            self._bookings.append(
                BookingRecord(
                    show_id=show_id,
                    customer_name=customer_name,
                    seats=int(seats),
                    zone=zone,
                    accessibility=accessibility,
                    confirmation_code=code,
                )
            )
            if code.startswith("BK-") and code[3:].isdigit():
                max_id = max(max_id, int(code[3:]))
        self._counter = max_id

    def list_shows(self) -> list[dict[str, Any]]:
        out = []
        for s in self._shows_config:
            sid = s["id"]
            out.append(
                {
                    **s,
                    "remaining_seats": self.remaining(sid),
                }
            )
        return out

    def list_bookings(self) -> list[dict[str, Any]]:
        return [b.to_dict() for b in self._bookings]

    def remaining(self, show_id: str) -> int:
        return self._capacity.get(show_id, 0) - self._used.get(show_id, 0)

    def book(
        self,
        show_id: str,
        seats: int,
        customer_name: str,
        zone: str,
        accessibility: str,
    ) -> BookingRecord:
        with _lock:
            cap = self._capacity.get(show_id)
            if cap is None:
                raise ValueError("UNKNOWN_SHOW")
            if seats < 1:
                raise ValueError("INVALID_SEATS")
            rem = cap - self._used[show_id]
            if seats > rem:
                raise ValueError("NOT_ENOUGH_SEATS")
            self._used[show_id] = self._used.get(show_id, 0) + seats
            self._counter += 1
            code = f"BK-{self._counter:05d}"
            rec = BookingRecord(
                show_id=show_id,
                customer_name=customer_name,
                seats=seats,
                zone=zone,
                accessibility=accessibility,
                confirmation_code=code,
            )
            self._bookings.append(rec)
            if self._db_path:
                with sqlite3.connect(self._db_path) as conn:
                    conn.execute(
                        "INSERT INTO bookings "
                        "(show_id, customer_name, seats, zone, accessibility, confirmation_code) "
                        "VALUES (?, ?, ?, ?, ?, ?)",
                        (
                            show_id,
                            customer_name,
                            seats,
                            zone,
                            accessibility,
                            code,
                        ),
                    )
                    conn.commit()
            return rec


def load_shows_yaml(base: Path) -> list[dict[str, Any]]:
    path = base / "data" / "shows.yaml"
    with open(path, encoding="utf-8") as f:
        data = yaml.safe_load(f) or {}
    shows = data.get("shows") or []
    if not shows:
        raise ValueError("shows.yaml must define a non-empty 'shows' list.")
    return shows


def _db_path_from_env(base: Path) -> Path | None:
    raw = (os.environ.get("THEATRE_DB") or "").strip()
    if raw:
        return Path(raw)
    default = base / "data" / "theatre.db"
    if os.environ.get("THEATRE_PERSIST", "").lower() in ("1", "true", "yes"):
        return default
    return None


def build_store(base: Path) -> ReservationStore:
    return ReservationStore(load_shows_yaml(base), db_path=_db_path_from_env(base))

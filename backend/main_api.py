"""
FastAPI backend for theatre reservations (Lab 6-style REST layer).
Run: uvicorn backend.main_api:app --reload --port 8000
"""
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

_BASE = Path(__file__).resolve().parents[1]
import sys

if str(_BASE) not in sys.path:
    sys.path.insert(0, str(_BASE))

from reservation_store import build_store  # noqa: E402

app = FastAPI(title="Theatre Reservation API", version="1.0.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

_store = build_store(_BASE)


class BookingIn(BaseModel):
    show_id: str
    seats: int = Field(ge=1, le=20)
    customer_name: str
    zone: str
    accessibility: str = "none"


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/shows")
def list_shows():
    return _store.list_shows()


@app.get("/reservations")
def list_reservations():
    return _store.list_bookings()


@app.post("/reservations")
def create_reservation(body: BookingIn):
    try:
        rec = _store.book(
            body.show_id,
            body.seats,
            body.customer_name,
            body.zone,
            body.accessibility,
        )
    except ValueError as e:
        code = str(e)
        if code == "NOT_ENOUGH_SEATS":
            raise HTTPException(status_code=409, detail=code) from e
        raise HTTPException(status_code=400, detail=code) from e
    return rec.to_dict()

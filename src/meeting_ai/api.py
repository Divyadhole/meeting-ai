from __future__ import annotations

import os
import uuid
from pathlib import Path

from fastapi import FastAPI, HTTPException, Query, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field

from .extractor import extract_meeting
from .store import MeetingStore

ROOT = Path(__file__).resolve().parents[2]
store = MeetingStore(os.getenv("MEETING_AI_DB", str(ROOT / "meeting_ai.db")))
app = FastAPI(title="Fathom++ API", version="0.1.0", description="Evidence-grounded meeting intelligence and evaluation.")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])


class IngestRequest(BaseModel):
    title: str = Field(min_length=1, max_length=120)
    transcript: str = Field(min_length=10)
    prompt_version: str = "v1"


class FeedbackRequest(BaseModel):
    rating: int = Field(ge=-1, le=1)
    correction: str | None = None


@app.get("/api/health")
def health() -> dict:
    return {"status": "ok", "service": "fathom-plus-plus"}


@app.post("/api/meetings")
def ingest(payload: IngestRequest) -> dict:
    meeting_id = uuid.uuid4().hex[:10]
    result = extract_meeting(meeting_id, payload.title, payload.transcript, payload.prompt_version)
    data = result.to_dict()
    store.save(meeting_id, payload.title, payload.transcript, data)
    return data


@app.get("/api/meetings")
def meetings() -> list[dict]:
    return store.all()


@app.get("/api/meetings/{meeting_id}")
def meeting(meeting_id: str) -> dict:
    if result := store.get(meeting_id):
        return result
    raise HTTPException(404, "Meeting not found")


@app.get("/api/search")
def search(q: str = Query(min_length=2)) -> list[dict]:
    return store.search(q)


@app.post("/api/meetings/{meeting_id}/feedback", status_code=204, response_class=Response)
def feedback(meeting_id: str, payload: FeedbackRequest) -> Response:
    if not store.get(meeting_id):
        raise HTTPException(404, "Meeting not found")
    store.feedback(meeting_id, payload.rating, payload.correction)
    return Response(status_code=204)


@app.get("/")
def dashboard() -> FileResponse:
    return FileResponse(ROOT / "docs" / "index.html")

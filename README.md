# Fathom++: Verifiable Meeting Intelligence

An end-to-end AI product prototype that turns speaker-labeled transcripts into evidence-grounded decisions, action items, risks, unanswered questions, participation analytics, and searchable organizational memory.

This is deliberately **not another chatbot**. Its central product bet is that meeting intelligence becomes trustworthy only when every extracted claim is inspectable and the system is measured against labeled ground truth.

## What is working

- Structured extraction with owners, deadlines, confidence, quotes, speakers, and timestamps
- Decision, action-item, risk, and unanswered-question detection
- Participation and topic analytics
- SQLite meeting store, ranked search, and human-feedback capture
- FastAPI endpoints with interactive OpenAPI documentation
- Versioned prompt artifact and reproducible benchmark corpus
- Precision, recall, F1, hallucination, JSON validity, latency, and cost reporting
- Responsive portfolio dashboard and live transcript analyzer
- Docker Compose services for API, Qdrant, and Redis
- Tests and GitHub Actions CI

The zero-cost deterministic extractor makes the whole product reproducible without an API key. It is a baseline—not a claim that rules outperform frontier models. Provider adapters and fine-tuning are the next experiment once real, consented labels exist.

## Quick start

```bash
python3 run_pipeline.py
python3 -m unittest discover -s tests -v

python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
make api
```

Open [http://localhost:8000](http://localhost:8000) for the product or [http://localhost:8000/docs](http://localhost:8000/docs) for the API.

## Architecture

```text
Audio / Zoom transcript
        │
        ▼
Transcription + diarization boundary
        │
        ▼
Normalized speaker turns ───────► SQLite transcript store
        │
        ▼
Versioned extraction pipeline
        │
        ├── decisions + evidence
        ├── actions + owners + deadlines
        ├── risks + unanswered questions
        └── topics + participation
        │
        ├────────► Search / Qdrant production boundary
        ├────────► Interactive API + dashboard
        └────────► Evaluation harness ──► launch gates
                                          │
Human corrections ◄───────────────────────┘
        │
        ▼
Reviewed fine-tuning dataset (LoRA/QLoRA experiment)
```

## API

| Method | Endpoint | Purpose |
|---|---|---|
| `POST` | `/api/meetings` | Analyze and persist a transcript |
| `GET` | `/api/meetings` | List meeting intelligence |
| `GET` | `/api/meetings/{id}` | Retrieve one result |
| `GET` | `/api/search?q=...` | Search meetings and extracted claims |
| `POST` | `/api/meetings/{id}/feedback` | Store rating or correction |
| `GET` | `/api/health` | Readiness check |

## Evaluation philosophy

Summary-only metrics can reward fluent fabrication. Fathom++ prioritizes field-level extraction scores and evidence coverage:

| Gate | Why it matters |
|---|---|
| Evidence precision ≥ 95% | Users can verify every claim |
| Action recall ≥ 85% | Commitments are the highest-value meeting artifact |
| JSON validity = 100% | Downstream product surfaces remain reliable |
| Hallucination ≤ 2% | Unsupported claims directly erode trust |
| Latency and cost | Quality must remain product-viable |

Run `python3 run_pipeline.py` to regenerate [`benchmark/results.json`](benchmark/results.json) from the checked-in labeled dataset. A production comparison should run the same examples across OpenAI, Claude, Gemini, and a LoRA-tuned open model, with repeated trials and confidence intervals.

## Product decisions and honest boundaries

- Evidence is displayed beside the claim because confidence scores alone are poorly calibrated and hard for users to interpret.
- Explicit statements are extracted; proposals are not silently promoted into decisions.
- Human corrections are captured but do not automatically enter training data. They first require consent, PII removal, and adjudication.
- The included corpus is intentionally small and synthetic. It proves the evaluation machinery, not production model quality.
- Whisper/pyannote, Qdrant, Postgres, Redis, and provider SDKs are production boundaries rather than fake integrations. The local MVP accepts diarized text and uses SQLite so reviewers can run it in minutes.

## Roadmap

1. Add consented real-user transcripts and double-annotated ground truth.
2. Implement provider adapters behind one typed extraction protocol.
3. Run prompt v1/v2 and model comparisons with error taxonomy.
4. Add Whisper large-v3 + pyannote ingestion for uploaded audio.
5. Add Qdrant hybrid retrieval and a Neo4j-backed cross-meeting graph.
6. Fine-tune Llama with LoRA only after the corrected dataset is large enough to justify it.

## Repository map

```text
src/meeting_ai/  extraction, storage, evaluation, and API
datasets/        labeled benchmark and generated outputs
prompts/         versioned extraction contracts
benchmark/       reproducible evaluation results
docs/            portfolio dashboard
tests/           unit and integration tests
.github/         continuous integration
```

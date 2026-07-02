# Fathom++: Verifiable Meeting Intelligence

[![CI](https://github.com/Divyadhole/meeting-ai/actions/workflows/ci.yml/badge.svg)](https://github.com/Divyadhole/meeting-ai/actions/workflows/ci.yml)
![Python](https://img.shields.io/badge/Python-3.12-3776AB?logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-0.115-009688?logo=fastapi&logoColor=white)
![License](https://img.shields.io/badge/license-MIT-17211b)

An end-to-end AI product prototype that turns speaker-labeled transcripts into evidence-grounded decisions, action items, risks, unanswered questions, participation analytics, and searchable organizational memory.

This is deliberately **not another chatbot**. Its central product bet is that meeting intelligence becomes trustworthy only when every extracted claim is inspectable and the system is measured against labeled ground truth.

> **Portfolio thesis:** meeting assistants should be evaluated as systems of record, not judged only by whether their summaries sound fluent.

## Product tour

1. Paste a speaker-labeled transcript into the live analyzer.
2. Inspect decisions, owners, deadlines, risks, questions, and supporting quotes.
3. Search across persisted meetings and watch workspace analytics update from real API data.
4. Rate an extraction; the transcript, prompt version, original output, and correction become a reviewable training candidate.
5. Run the benchmark to compare extraction quality, grounding, latency, validity, and cost.

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
| `GET` | `/api/analytics` | Aggregate workspace activity and topics |
| `GET` | `/api/feedback` | Export reviewed fine-tuning candidates |
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

### Reproducible baseline result

| Model | Prompt | Action F1 | Decision F1 | Hallucination | JSON validity | Cost |
|---|---:|---:|---:|---:|---:|---:|
| Deterministic baseline | v1 | 1.000 | 1.000 | 0.0% | 100% | $0.00 |

These scores are deliberately reported with their boundary: five synthetic, pattern-controlled meetings. They validate the harness and product plumbing—not generalization to real calls. The next credible result requires consented real transcripts, independent annotation, and confidence intervals.

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

## Interview walkthrough (3 minutes)

- **0:00–0:30:** Explain the trust problem and show evidence beside a decision.
- **0:30–1:15:** Analyze a transcript and inspect owners, deadlines, open questions, and risks.
- **1:15–1:45:** Search across meetings and show live workspace analytics.
- **1:45–2:30:** Open the evaluation lab and explain why evidence precision and action recall are launch gates.
- **2:30–3:00:** Capture human feedback and explain the privacy-reviewed fine-tuning flywheel.

## Privacy and responsible use

Meeting content can contain sensitive personal and company information. A production deployment needs participant consent, encryption, retention controls, deletion workflows, role-based access, PII redaction, regional storage choices, and audit logging. Human corrections must never flow directly into training without review and explicit data-use permission.

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

## License

MIT — see [`LICENSE`](LICENSE).

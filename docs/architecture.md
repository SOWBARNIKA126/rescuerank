# Architecture

```mermaid
flowchart LR
    A[WhatsApp / Telegram bot<br/>SMS · web form] --> B[Voice to text<br/>Whisper]
    B --> C[Language clean-up<br/>Tamil · English · Tanglish]
    C --> D[Extraction<br/>place · people · need · who is at risk]
    D --> E[Geocode<br/>OpenStreetMap + landmark list]
    E --> F[De-duplicate<br/>merge repeat reports]
    F --> G[Trust check<br/>senders · forwards]
    G --> H[Urgency score 0-100<br/>with reasons]
    H --> I[Dashboard<br/>ranked queue + live map]
    I --> J{Officer approves?}
    J -- yes --> K[Team dispatched<br/>WhatsApp reply to citizen]
    J -- no --> I
```

## Stage by stage

| Stage | Purpose | In this repo today | Planned |
|---|---|---|---|
| Intake | Get messages in from people on weak networks | `POST /messages` API | WhatsApp Cloud API / Telegram bot, SMS gateway |
| Voice to text | Handle voice notes | not built | Whisper |
| Extraction | Turn free text into structured facts | `extract.py` (rules: English, Tanglish, some Tamil script) | LLM extractor returning the same `Extraction` object |
| Geocoding | Put reports on a map | `gazetteer.py` (14 Chennai localities, approximate) | OpenStreetMap Nominatim + landmark list |
| De-duplication | One incident = one card | `dedup.py` (same place + street + time window + wording) | multilingual embeddings (LaBSE) + geo-time clustering |
| Trust | Limit rumours | `pipeline.py` (sender count, chain-forward detection) | source reputation, cross-checks with official alerts |
| Urgency score | Rank by who needs help first | `score.py` (explainable, example weights) | weights tuned with disaster-management officers |
| Dashboard | Show the ranked queue on a map | concept image only | React + Leaflet, nearest-team routing (OSRM) |

## Design decisions

* **Explainable first.** Every point in the urgency score has a written reason, so an officer can trust or override it.
* **Human in the loop.** The system ranks and suggests. It never dispatches by itself.
* **One interface per stage.** The rule-based extractor and the planned LLM extractor both return `Extraction`, so swapping one for the other touches no other file.
* **Works offline.** The baseline needs no API keys, so the demo and tests run anywhere.

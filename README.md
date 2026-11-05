# WORKLENS (Workload Intelligence Platform)

WORKLENS is an enterprise-grade workload intelligence platform engineered to ingest, enrich, validate, and analyze automation assessment datasets deterministically and with AI-assisted qualitative insights.

---

## Key Capabilities

- **M1 — Deterministic Enrichment:** Strict 6-priority formula evaluation for monthly/annualized workload savings and reduction percentages with zero arithmetic guessing.
- **M2 — Change Detection Engine:** Exact `activity_id` tracking, deterministic SHA-256 content hashing, and delta classification (`UNCHANGED`, `MODIFIED`, `ADDED`, `DELETED`, `REVIEW_REQUIRED`).
- **M3 — AI Assessment Reviewer:** Qualitative reviews across Data Quality, Assessment Consistency, and Automation Opportunities with offline mock mode by default and local privacy sanitization.
- **Model Context Protocol (MCP) Integration:** Direct agent tool integration for natural language queries and automated workload discovery.
- **Interactive Web Dashboard:** Modern React + TypeScript + Vite + Tailwind CSS interface for real-time filtering, KPI visualization, manual assessment upload, and diff inspection.

---

## Repository Structure

```text
worklens/
├── .env.example              # Environment variables template
├── .gitignore                # Git ignore patterns for Python & Node
├── README.md                 # Project documentation and developer guide
├── docs/                     # Architectural specifications and ADRs
│   └── ARCHITECTURE.md       # High-level architecture and system design
├── backend/                  # Python FastAPI Backend
│   ├── pyproject.toml        # Backend build configuration & dependencies
│   ├── requirements.txt      # Pinned backend dependencies
│   ├── pytest.ini            # Pytest configuration
│   ├── app/
│   │   ├── main.py           # FastAPI entrypoint
│   │   ├── config.py         # Pydantic BaseSettings configuration
│   │   ├── api/              # API router hierarchy (/api/v1)
│   │   ├── core/             # Core deterministic engines (M1, M2, M3)
│   │   ├── models/           # Pydantic schemas and domain types
│   │   └── services/         # In-memory BreakdownDataStore and MCP service
│   └── tests/                # Automated pytest suite
└── frontend/                 # React + TypeScript + Vite Dashboard
    ├── package.json          # Node dependencies and scripts
    ├── tsconfig.json         # TypeScript compiler configuration
    ├── vite.config.ts        # Vite build tool configuration
    ├── tailwind.config.js    # Tailwind CSS styling configuration
    ├── index.html            # Single-page application root HTML
    └── src/                  # React application source code
        ├── App.tsx           # Main application shell
        ├── main.tsx          # DOM mount entrypoint
        ├── index.css         # Tailwind utility imports
        ├── components/       # Reusable UI widgets and data views
        └── types/            # TypeScript interface definitions
```

---

## Getting Started

### Prerequisites

- **Python:** 3.11+ (Python 3.14 supported)
- **Node.js:** 20+ (Node.js 24 supported)
- **Package Managers:** `pip` and `npm`

### Backend Setup

```bash
cd backend
python -m venv .venv
# On Windows:
.venv\Scripts\activate
# On Linux/macOS:
# source .venv/bin/activate

pip install -r requirements.txt
pytest
```

Run the backend server:

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

The interactive OpenAPI documentation will be available at: `http://localhost:8000/docs`.

### Frontend Setup

```bash
cd frontend
npm install
npm run dev
```

The frontend dashboard will be available at: `http://localhost:5173`.

---

## Architectural Principles

1. **Source Immutability:** Raw input datasets are strictly read-only.
2. **Logic Separation:** Deterministic enrichment metrics are never calculated or overwritten by AI/LLMs.
3. **Smallest Complete Solution (Ponytail / YAGNI):** No unnecessary database layers or complex middleware when lightweight in-memory stores and structured files solve the requirement reliably.
4. **Offline First:** Fully functional in offline mock mode without requiring live external LLM API keys.

---

## License

Proprietary — Internal Enterprise Automation Platform.

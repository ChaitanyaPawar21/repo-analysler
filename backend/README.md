# Repo Analyser — Backend

A production-grade GitHub repository analysis platform built with **FastAPI**, **PostgreSQL**, **FAISS**, and **NetworkX**.

## 🏗️ Architecture

```
backend/
├── api/              # HTTP layer — versioned REST endpoints
│   └── v1/
│       ├── endpoints/
│       │   ├── analyze.py        # Trigger & poll analysis
│       │   ├── repo.py           # Repository CRUD
│       │   ├── chat.py           # AI-powered codebase chat
│       │   ├── graph.py          # Dependency graph exploration
│       │   └── critical_files.py # Critical file identification
│       └── router.py             # V1 router aggregator
│
├── core/             # Application-wide configuration
│   ├── config.py     # Pydantic-settings (env vars)
│   ├── constants.py  # Enums, patterns, thresholds
│   └── logger.py     # Structured logging (structlog)
│
├── services/         # Business logic layer
│   ├── repo_service.py       # Repository management
│   ├── parser_service.py     # Code parsing (AST)
│   ├── graph_service.py      # NetworkX dependency graphs
│   ├── analysis_service.py   # Pipeline orchestrator
│   ├── ai_service.py         # LLM / RAG chat
│   └── embedding_service.py  # Vector embedding generation
│
├── db/               # Data layer
│   ├── postgres.py   # Async SQLAlchemy engine & sessions
│   └── vector_store.py # FAISS index management
│
├── models/           # ORM models (SQLAlchemy)
│   ├── repo.py       # Repository table
│   └── analysis.py   # Analysis table
│
├── schemas/          # Pydantic request/response schemas
│   ├── repo_schema.py
│   └── chat_schema.py
│
├── utils/            # Shared utilities
│   ├── github_utils.py  # GitHub API, URL parsing, cloning
│   └── file_utils.py    # File I/O, binary detection
│
├── tests/            # Pytest test suite
│   ├── conftest.py   # Shared fixtures
│   └── test_health.py
│
├── main.py           # FastAPI app factory & lifespan
├── requirements.txt  # Python dependencies
├── .env              # Environment variables (not committed)
└── README.md
```

## ⚡ Key Design Decisions

| Decision | Rationale |
|---|---|
| **FastAPI + async** | Non-blocking I/O for GitHub API calls, DB queries, and LLM requests |
| **BackgroundTasks** | Simple async processing without Redis/Celery infrastructure overhead |
| **FAISS** | Fast in-memory vector search for code embeddings |
| **NetworkX** | Rich graph algorithms (centrality, PageRank) for dependency analysis |
| **Pydantic v2** | Strict type validation at API boundaries and configuration |
| **structlog** | Structured JSON logs ready for production log aggregation |

## 🔄 Celery Migration Path

The codebase is designed for easy migration to Celery when scaling requires it:

1. **Install**: Add `celery` and `redis` to `requirements.txt`
2. **Configure**: Add `CELERY_BROKER_URL` and `CELERY_RESULT_BACKEND` to `.env`
3. **Create worker**: Add `celery_app.py` with Celery instance configuration
4. **Migrate tasks**: In `analyze.py`, replace:
   ```python
   # Before (BackgroundTasks)
   background_tasks.add_task(_run_analysis_background, analysis.id, db, vector_store)

   # After (Celery)
   from tasks import run_analysis_task
   run_analysis_task.delay(str(analysis.id))
   ```
5. **Service layer**: No changes needed — `AnalysisService` works identically

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- PostgreSQL 15+
- Git

### Setup

```bash
# 1. Create virtual environment
python -m venv venv
source venv/bin/activate   # Linux/Mac
venv\Scripts\activate      # Windows

# 2. Install dependencies
pip install -r requirements.txt

# 3. Configure environment
cp .env.example .env
# Edit .env with your database URL, API keys, etc.

# 4. Start PostgreSQL and create the database
createdb repo_analyser

# 5. Run the application
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### API Documentation
Once running, visit:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

### Run Tests
```bash
# Create test database first
createdb repo_analyser_test

# Run tests
pytest -v
```

## 📡 API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/health` | Health check |
| `POST` | `/api/v1/repos/` | Register a repository |
| `GET` | `/api/v1/repos/` | List repositories |
| `GET` | `/api/v1/repos/{id}` | Get repository details |
| `DELETE` | `/api/v1/repos/{id}` | Soft-delete repository |
| `POST` | `/api/v1/analyze/` | Trigger analysis (async) |
| `GET` | `/api/v1/analyze/{id}` | Get analysis status |
| `POST` | `/api/v1/chat/` | Chat with codebase |
| `GET` | `/api/v1/graph/{repo_id}` | Get dependency graph |
| `GET` | `/api/v1/graph/{repo_id}/subgraph` | Get localized subgraph |
| `GET` | `/api/v1/critical-files/{repo_id}` | Get critical files |

## 📝 License

MIT

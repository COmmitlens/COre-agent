# Project Guidelines

## Overview

AI backend service that uses Azure OpenAI (GPT-4o-mini) via LangChain to explain Git commit file changes. Stateless FastAPI app streaming LLM responses over SSE.

## Code Style

- **camelCase** for Pydantic request model fields (matches JS frontend consumer) — see [routes.py](ai-backend/app/api/routes.py)
- Async generators for all streaming patterns — see [summary_chain.py](ai-backend/app/chains/summary_chain.py)
- No `__init__.py` files; relies on implicit namespace packages
- Dependencies in `requirements.txt` are unpinned

## Architecture

```
ai-backend/
├── main.py                  # Uvicorn launcher (dev entry point, reload=True)
├── app/
│   ├── main.py              # FastAPI app factory, loads .env, mounts router, /health
│   ├── api/routes.py        # HTTP endpoints (POST /explain-commit-file-change)
│   └── chains/              # LangChain LLM logic (one chain per file)
│       └── summary_chain.py # Azure OpenAI streaming + non-streaming wrappers
```

- **Layered**: entry point → FastAPI app → API routes → LLM chains
- `chains/` isolates all LLM orchestration from HTTP handling
- Single POST endpoint accepts `{systemPrompt, userPrompt}`, returns `text/event-stream`
- Two entry points exist: root `main.py` (dev w/ reload) and `app/main.py` (direct)

## Build and Test

```bash
# Install dependencies
pip install -r ai-backend/requirements.txt

# Run dev server (port 9000, auto-reload)
cd ai-backend && python main.py

# Or directly via uvicorn
cd ai-backend && uvicorn app.main:app --reload --port 9000

# Production via PM2
pm2 start ecosystem.config.json

# Docker
docker build -t ai-backend ai-backend/
docker run -p 9000:9000 --env-file ai-backend/.env ai-backend
```

No test suite exists yet. Health check: `GET /health` → `{"status": "ok"}`.

## Project Conventions

- Request models use **camelCase** fields (`systemPrompt`, `userPrompt`), not snake_case
- Streaming responses use `StreamingResponse` with `text/event-stream` media type
- LLM config (model, deployment, API version) is hardcoded in `summary_chain.py`, not env-driven
- PM2 (`ecosystem.config.json`) manages the Python process in production — unusual but intentional
- Default port is **9000**, configurable via CLI args in `main.py`

## Integration Points

- **Azure OpenAI**: `AzureChatOpenAI` — endpoint and API key loaded from `.env`
- **LangChain**: `ChatPromptTemplate` with system/human message pairs
- No database — fully stateless
- Consumed by a frontend client (SSE streaming, camelCase API contract)

## Security

- Secrets managed via `.env` file: `AZURE_OPENAI_API_KEY`, `ENDPOINT_URL`, `OPENAI_API_KEY`
- `.env` is gitignored — never commit it
- Dockerfile declares env vars as empty, expecting runtime injection (`-e` or `--env-file`)
- **No auth middleware** on endpoints — relies on network-level access control
- **No CORS configured** — must be added if serving browser clients directly

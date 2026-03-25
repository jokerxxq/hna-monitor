# HNA Flight Monitor (Web)

A FastAPI-based web app to monitor flight prices and push WeChat alerts.

## Features
- Create/delete/enable/disable monitoring tasks
- Background scheduler polling
- Price threshold alerting with de-duplication
- WeChat push via Server酱
- SQLite persistence + web logs
- Variflight MCP stdio provider (recommended)

## Quick Start (Local)

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
uvicorn app.main:app --reload
```

Open `http://127.0.0.1:8000`

## Variflight MCP Configuration

1. Install Node.js (required for `npx`).
2. Fill `.env` with your MCP key:

```env
PRICE_PROVIDER=variflight_mcp
VARIFLIGHT_API_KEY=your_key_here
VARIFLIGHT_MCP_COMMAND=npx
VARIFLIGHT_MCP_ARGS=-y @variflight-ai/variflight-mcp
```

3. In web form, input city codes (e.g. `SZX` -> `KMG`) and date.

## Fallback

If you need quick local testing without MCP key:

```env
PRICE_PROVIDER=mock
```

## Ubuntu Deployment

- Upload code to server
- Install Python + Node.js
- Create virtualenv and install dependencies
- Fill `.env`
- Run with systemd service template under `systemd/hna-monitor.service`

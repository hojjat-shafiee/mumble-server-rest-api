# Mumble Server REST API

A modern, high-performance RESTful API built with **FastAPI** to manage and administer virtual Mumble (**Murmur**) VoIP servers via ZeroC Ice RPC.

---

## Features

- **FastAPI & Uvicorn**: High throughput, automated interactive Swagger UI (`/docs`) and ReDoc (`/redoc`).
- **Threadpool Offloading**: ZeroC Ice blocking socket calls run automatically in worker threadpools, preventing asyncio event loop starvation.
- **Graceful Lifecycle Management**: Non-blocking startup with FastAPI lifespan handlers; automatic reconnection and graceful communicator teardown.
- **Security Hardening**:
  - Optional API Key / Bearer Token authentication (`API_KEY`).
  - Automatic password masking (`MASK_PASSWORDS=true`).
- **Standard RESTful API + Legacy Support**:
  - Full support for RESTful routes (`/servers`, `/servers/{id}`, `/servers/{id}/start`, `/servers/{id}/stop`, `/servers/{id}/restart`, `/servers/{id}/logs`).
  - Backward compatibility aliases for legacy `Murmur-REST` query/RPC endpoints (`/server/getAllServers`, `/server/getServerDetail?id=1`, `/server/createServer`, etc.).
- **Turnkey Docker Compose**: Single command boots both Murmur server and the REST API connected on an internal Docker bridge network.
- **Comprehensive Test Harness**: Mock-backed `pytest` suite enabling rapid testing across all platforms without native ZeroC Ice C++ libraries.

---

## Architecture

```
HTTP Client / Frontend
        │
        ▼ (Port 2332)
┌──────────────────────────────────────────────┐
│ FastAPI Application                          │
│ ├─ Lifespan & IceManager                     │
│ ├─ RESTful Endpoints (/servers/*)            │
│ └─ Threadpool Dispatch (run_in_threadpool)   │
└──────────────────────┬───────────────────────┘
                       │ ZeroC Ice RPC (Port 6502)
                       ▼
┌──────────────────────────────────────────────┐
│ Murmur Voice Server (Mumble)                 │
│ ├─ Virtual Server 1 (Voice Port 64738)       │
│ └─ Virtual Server 2 ...                      │
└──────────────────────────────────────────────┘
```

---

## Quickstart with Docker Compose

To boot both the **Murmur server** and the **REST API** together:

```bash
docker compose up -d --build
```

- **Interactive API Docs (Swagger)**: [http://localhost:2332/docs](http://localhost:2332/docs)
- **Alternative Docs (ReDoc)**: [http://localhost:2332/redoc](http://localhost:2332/redoc)
- **Health Check**: [http://localhost:2332/healthz](http://localhost:2332/healthz)

---

## Configuration

Configuration is managed via environment variables (or `.env` file):

| Variable | Default | Description |
| :--- | :--- | :--- |
| `MURMUR_ICE_HOST` | `localhost` | Murmur Ice hostname or container address |
| `MURMUR_ICE_PORT` | `6502` | Murmur Ice listening port |
| `MURMUR_ICE_TIMEOUT` | `1000` | Ice invocation timeout in milliseconds |
| `ICE_SECRET` | `""` | Murmur Ice administrative secret (from `murmur.ini`) |
| `ICE_MESSAGE_SIZE` | `1024` | Maximum Ice message size (KB) |
| `API_KEY` | `""` | Optional API Key. If set, required via `X-API-Key` or `Authorization: Bearer <key>` |
| `MASK_PASSWORDS` | `true` | When true, masks server passwords in API detail responses (`***`) |

---

## API Endpoints

### Health & Version
- `GET /` — API version and service status.
- `GET /healthz` — Service health check and Murmur Ice connectivity probe.
- `GET /servers/murmur-version` — Murmur server Ice version.

### Server Management
- `GET /servers` — List all virtual servers and statistics.
- `POST /servers` — Create and boot a new virtual server.
- `GET /servers/{id}` — Get full details, channel tree, and active users for a virtual server.
- `PATCH /servers/{id}` — Update virtual server configuration.
- `DELETE /servers/{id}` — Stop and delete a virtual server.
- `POST /servers/batch-delete` — Batch delete multiple virtual servers by ID list.
- `DELETE /servers/all` — Stop and delete all virtual servers.

### Actions & Logs
- `POST /servers/{id}/start` — Boot an inactive server.
- `POST /servers/{id}/stop` — Shut down an active server.
- `POST /servers/{id}/restart` — Restart a virtual server.
- `GET /servers/{id}/logs` — Retrieve timestamped server logs.

---

## Running Tests

Run the complete test harness locally:

```bash
pip install -r requirements-dev.txt
pytest -v
```

---

## License

This project is licensed under the MIT License.

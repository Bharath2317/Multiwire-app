# MultiWire Production System

Flask app for logging multi-wire saw production runs. Each Multi Wire moves through
**NEW SET → AFTER REPLASTIFICATION → COMPLETED**, with daily entries per stage and
an Excel export built from `backend/excel/template.xlsx`.

## Run locally

```bash
cd backend
pip install -r requirements.txt   # add requirements-mssql.txt for SQL Server
cp .env.example .env      # then edit; set APP_ENV=development for local use
python app.py             # http://localhost:5000
```

## Deploy

Required environment variables (see `backend/.env.example`):

| Variable | Purpose |
|---|---|
| `APP_ENV=production` | Enables strict checks and secure cookies |
| `SECRET_KEY` | Long random string (app refuses to start with the default) |
| `APP_PASSWORD` | Shared login password (app refuses to start without it) |
| `DATABASE_SERVER` / `DATABASE_NAME` (+ `DATABASE_USER`/`DATABASE_PASSWORD`) | SQL Server |
| `DATABASE_URL` | Optional: any SQLAlchemy URL, overrides the above |

**Windows / any OS:** `cd backend && python serve.py` (waitress, port 8000).
**Docker:** `docker build -t multiwire . && docker run -p 8000:8000 --env-file backend/.env multiwire`
(image includes ODBC Driver 18).

Put it behind HTTPS (reverse proxy such as nginx, Caddy or IIS) — session cookies are
marked `Secure` in production. Health check: `/healthz`.

Tables and the newest columns are created automatically on first start.

## Free hosting (Render + free Postgres)

`render.yaml` is included. Free hosts can't reach a private SQL Server and their disks
are wiped on restart, so use a hosted Postgres.

1. Create a free Postgres (e.g. [Neon](https://neon.tech) or Render Postgres) and copy its connection string.
2. On [render.com](https://render.com): **New → Blueprint** → pick this GitHub repo.
3. When prompted, set `APP_PASSWORD` and `DATABASE_URL` (`SECRET_KEY` is generated).
4. Deploy. Tables are created on first start. Free services sleep after ~15 min idle, so the first load is slow.

Data does not migrate automatically from SQL Server; the hosted copy starts empty.

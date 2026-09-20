# Sentiment Classification API (FastAPI v2)

A FastAPI rebuild of the original Flask customer review sentiment classifier —
adds JWT authentication, a proper REST structure, and Docker-based deployment.

## Option A — Run locally with your existing Laragon MySQL

1. Start Laragon, make sure MySQL is running, and create a database called `sentiment_db`
   (Laragon's phpMyAdmin, or `mysql -u root -e "CREATE DATABASE sentiment_db;"`).
2. Copy `.env.example` to `.env` and adjust `DATABASE_URL` if your Laragon MySQL user/password differ
   from the default `root` with no password.
3. Create a virtual environment and activate it:
   - Windows: `python -m venv venv` then `venv\Scripts\activate`
4. Install dependencies: `pip install -r requirements.txt`
5. Run the server: `uvicorn app.main:app --reload`
6. Open **http://127.0.0.1:8000/docs** — this is your interactive Swagger UI. You can register a
   user, log in, copy the token, and call `/predict` right from the browser.

## Option B — Run with Docker (no local MySQL needed)

```
docker compose up --build
```

This spins up the API and a MySQL container together. Same URL: http://127.0.0.1:8000/docs

## Wiring in your real model

Open `app/routers/predict.py` — the `classify_sentiment()` function is a stub. Replace it with
your trained Naive Bayes model + vectorizer (see the TODO comments at the top of the file).
Export your model from your thesis code with `joblib.dump(...)`, drop the `.pkl` files into an
`ml/` folder here, and load them at the top of `predict.py`.

## What's already covered

- JWT auth: `POST /auth/register`, `POST /auth/login`
- Protected endpoint: `POST /predict` (requires a Bearer token)
- History: `GET /predict/history`
- Auto-generated docs at `/docs`, validated request/response models via Pydantic

## Suggested next steps

1. Plug in the real model (above).
2. Write a few tests with `pytest` + FastAPI's `TestClient` (register → login → predict → assert response).
3. Push to GitHub with a clear README and a screenshot/GIF of the `/docs` page.
4. Deploy: Railway or Render both have free tiers and can host the API + a managed MySQL/Postgres
   database. Point `DATABASE_URL` at their managed database instead of localhost.
5. Once deployed, add the live URL and GitHub link to your LinkedIn Projects entry.

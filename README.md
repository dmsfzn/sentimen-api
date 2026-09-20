# Sentiment Classification API (v2 — FastAPI + JWT)

A REST API rebuild of my original Flask customer review sentiment classifier, same trained
Naive Bayes model and Indonesian text preprocessing pipeline, now served through a proper
REST layer with JWT authentication, request/response validation, auto-generated docs, and
Docker support.

**Original Flask version (v1, built for my thesis):** `github.com/dmsfzn/Tugas-Akhir`

This project doesn't retrain or change the model — it re-engineers how the model is *served*.
The dataset, the trained Naive Bayes model, and the 85.6% accuracy result all carry over
unchanged from v1.

## What's new compared to v1

| | v1 (Flask) | v2 (this repo) |
|---|---|---|
| Framework | Flask | FastAPI |
| Auth | None | JWT (register/login) |
| API style | Informal calls | REST endpoints |
| Validation | Manual | Pydantic schemas |
| Docs | None | Auto-generated at `/docs` |
| Deployment | Local only | Dockerized |

## Tech stack

- **FastAPI** + **Uvicorn** — web framework and server
- **SQLAlchemy** + **PyMySQL** — ORM and MySQL driver
- **python-jose** + **bcrypt** — JWT tokens and password hashing
- **scikit-learn** + **joblib** — loading the trained Naive Bayes model and vectorizer
- **Sastrawi** — Indonesian stopword removal
- **stemmid** — Indonesian stemming

## Text preprocessing pipeline

New review text goes through the same cleaning steps used before training, so it lines up
with what the vectorizer's vocabulary actually knows:

```
lowercase -> normalize elongation ("mantapp" -> "mantap") -> remove stopwords (Sastrawi) -> stem (stemmid)
```

The elongation-normalization step is new in v2 — it collapses repeated letters used for
emphasis in informal reviews (`"mantapp"`, `"kerennnn"`) so slang spellings map onto words
the model already recognizes, instead of being treated as unknown and ignored. Trade-off: a
few real Indonesian words with a genuine double letter (`"maaf"`, `"saat"`) get affected too;
in practice this has minimal impact since they aren't strong sentiment words.

## Option A — Run locally with your existing Laragon MySQL

1. Start Laragon, make sure MySQL is running, and create a **new** database — don't reuse
   your v1 database name, to keep the two projects' data fully separate. E.g. `sentiment_db_v2`.
2. Copy `.env.example` to `.env` and set `DATABASE_URL` to match (adjust user/password if
   yours differ from Laragon's default `root` with no password).
3. Create and activate a virtual environment:
   - Windows: `python -m venv venv` then `venv\Scripts\activate`
4. Install dependencies: `pip install -r requirements.txt`
   (this includes a GitHub-based install for `stemmid`, so it needs an internet connection)
5. Run the server: `uvicorn app.main:app --reload`
6. Open **http://127.0.0.1:8000/docs** — interactive Swagger UI. Register a user, log in, copy
   the token into the "Authorize" button, and call `/predict` right from the browser.

## Option B — Run with Docker (no local MySQL needed)

```
docker compose up --build
```

Spins up the API and a MySQL container together. Same URL: http://127.0.0.1:8000/docs

## Wiring in your trained model

1. From your v1 project, export the trained model and vectorizer once with:
   ```python
   import joblib
   joblib.dump(model, "naive_bayes_model.pkl")
   joblib.dump(vectorizer, "vectorizer.pkl")
   ```
2. Create an `ml/` folder in this project (same level as `app/`).
3. Copy both `.pkl` files in, keeping those exact filenames.
4. Restart `uvicorn` — the model loads once at startup. Without these files, `/predict` still
   runs using placeholder logic, so the API stays testable at every stage.

## API endpoints

| Method | Path | Auth required | Description |
|---|---|---|---|
| POST | `/auth/register` | No | Create an account |
| POST | `/auth/login` | No | Get a JWT access token |
| POST | `/predict` | Yes | Classify a review, save it to history |
| GET | `/predict/history` | Yes | List your past predictions |
| GET | `/docs` | No | Interactive Swagger UI |

## Known limitations

- The Naive Bayes / bag-of-words approach can't generalize to word forms it never saw in
  training. Elongation normalization helps with slang emphasis, but genuine typos or new
  vocabulary still won't be recognized.
- Confidence scores near `0.50` indicate the model found little to no recognizable signal in
  the input — not that the sentiment is uncertain.

## Suggested next steps

1. Write tests with `pytest` + FastAPI's `TestClient` (register → login → predict → assert).
2. Push to GitHub with a screenshot or GIF of the `/docs` page.
3. Deploy to Railway or Render (both have free tiers with managed MySQL/Postgres) — point
   `DATABASE_URL` at their managed database instead of localhost.
4. Add the live URL and this repo's link to your LinkedIn Projects entry.

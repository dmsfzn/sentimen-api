import os
from typing import List, Tuple

import joblib
from fastapi import APIRouter, Depends
from Sastrawi.StopWordRemover.StopWordRemoverFactory import StopWordRemoverFactory
from sqlalchemy.orm import Session
from stemmid import Stemmer

from .. import models, schemas
from ..auth import get_current_user
from ..database import get_db

router = APIRouter(prefix="/predict", tags=["predict"])

_stemmer = Stemmer()
_stopword_remover = StopWordRemoverFactory().create_stop_word_remover()

# Drop your two exported files here: ml/naive_bayes_model.pkl and ml/vectorizer.pkl
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))  # sentiment-api-starter/
ML_DIR = os.path.join(BASE_DIR, "ml")
MODEL_PATH = os.path.join(ML_DIR, "naive_bayes_model.pkl")
VECTORIZER_PATH = os.path.join(ML_DIR, "vectorizer.pkl")

try:
    model = joblib.load(MODEL_PATH)
    vectorizer = joblib.load(VECTORIZER_PATH)
except FileNotFoundError:
    # Lets the API still start and be testable before you've added the real files.
    model = None
    vectorizer = None


def preprocess_text(text: str) -> str:
    """
    Mirrors the pipeline in your Flask preprocess_data module:
    lowercase -> remove stopwords (Sastrawi) -> stem (stemmid).

    ASSUMPTION: stopwords removed BEFORE stemming. If your original code did
    it the other way around (stem first, then remove stopwords), swap the
    two lines below — the order has to match exactly or the vectorizer's
    vocabulary won't line up with what you send it here.
    """
    text = text.lower()                       # stemmid only stems lowercase input reliably
    text = _stopword_remover.remove(text)      # drop "yang", "dan", "di", etc.
    text = _stemmer.loads(text)                # reduce remaining words to root form
    return text


def classify_sentiment(text: str) -> Tuple[str, str]:
    if model is None or vectorizer is None:
        sentiment = "positive" if "good" in text.lower() else "negative"
        return sentiment, "n/a (model not loaded — add ml/*.pkl files)"

    cleaned = preprocess_text(text)
    vec = vectorizer.transform([cleaned])
    pred = model.predict(vec)[0]
    proba = model.predict_proba(vec).max()
    return str(pred), f"{proba:.2f}"


@router.post("", response_model=schemas.PredictionOut)
def predict(
    review: schemas.ReviewIn,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    sentiment, confidence = classify_sentiment(review.text)

    record = models.Prediction(
        review_text=review.text,
        sentiment=sentiment,
        confidence=confidence,
        owner_id=current_user.id,
    )
    db.add(record)
    db.commit()
    db.refresh(record)
    return record


@router.get("/history", response_model=List[schemas.PredictionOut])
def history(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    return (
        db.query(models.Prediction)
        .filter(models.Prediction.owner_id == current_user.id)
        .order_by(models.Prediction.created_at.desc())
        .all()
    )

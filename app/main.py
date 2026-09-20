from fastapi import FastAPI

from . import models
from .database import engine
from .routers import auth, predict

models.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Sentiment Classification API",
    description="FastAPI rebuild of the customer review sentiment classifier (v2, with auth).",
    version="2.0.0",
)

app.include_router(auth.router)
app.include_router(predict.router)


@app.get("/")
def root():
    return {"status": "ok", "message": "Sentiment Classification API is running"}

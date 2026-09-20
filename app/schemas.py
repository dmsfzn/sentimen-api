from datetime import datetime
from typing import Optional

from pydantic import BaseModel, EmailStr


class UserCreate(BaseModel):
    email: EmailStr
    password: str


class UserOut(BaseModel):
    id: int
    email: EmailStr
    created_at: datetime

    class Config:
        from_attributes = True


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class ReviewIn(BaseModel):
    text: str


class PredictionOut(BaseModel):
    id: int
    review_text: str
    sentiment: str
    confidence: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True

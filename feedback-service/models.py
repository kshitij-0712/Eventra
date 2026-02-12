from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class FeedbackOut(BaseModel):
    id: int
    event_id: int
    user_id: Optional[int] = None
    student_name: Optional[str] = None
    srn: Optional[str] = None
    rating: int
    comments: Optional[str] = None
    submitted_at: Optional[datetime] = None


class FeedbackCreate(BaseModel):
    event_id: int
    user_id: int
    rating: int
    comments: Optional[str] = None


class AverageRatingOut(BaseModel):
    event_id: int
    average_rating: float
    total_reviews: int

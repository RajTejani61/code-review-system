from pydantic import BaseModel
from typing import Optional
from datetime import datetime

# Review Schemas
class ReviewSummary(BaseModel):
    id: int
    language: Optional[str]
    status: str
    overall_score: Optional[int]
    created_at: datetime

    class Config:
        from_attributes = True

class ReviewDetail(BaseModel):
    id: int
    user_id: int
    code: str
    language: Optional[str]
    status: str
    error_message: Optional[str]
    
    security_review: Optional[str]
    performance_review: Optional[str]
    logic_review: Optional[str]
    style_review: Optional[str]
    
    final_report: Optional[str]
    overall_score: Optional[int]
    created_at: datetime

    class Config:
        from_attributes = True

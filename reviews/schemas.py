from pydantic import BaseModel, ConfigDict
from typing import Optional
from datetime import datetime

# Review Schemas
class ReviewSummary(BaseModel):
    id: int
    language: Optional[str]
    status: str
    overall_score: Optional[int]
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

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

    model_config = ConfigDict(from_attributes=True)

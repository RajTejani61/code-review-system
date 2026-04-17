from fastapi import APIRouter, Depends, BackgroundTasks, HTTPException, status, UploadFile, File, Form
from sqlalchemy.orm import Session
from database.database import get_db

from agents.orchestrator_agent import run_review
from users.models import User
from reviews.models import Review
from reviews.schemas import ReviewDetail

router = APIRouter(
    prefix="/reviews",
    tags=["Reviews"]
)

# Background Task 
async def process_review_background(review_id: int, db: Session):
    """Runs the full agent review in the background and updates the DB."""
    try:
        # 1. Fetch the review row
        db_review = db.query(Review).filter(Review.id == review_id).first()
        if not db_review:
            return

        # 2. Update status to 'processing'
        db_review.status = "processing"
        db.commit()

        # 3. Run the LangGraph orchestrator
        final_report = await run_review(db_review.code, db_review.language)

        # 4. Save results and update status to 'completed'
        db_review.security_review = final_report.security.model_dump_json()
        db_review.performance_review = final_report.performance.model_dump_json()
        db_review.logic_review = final_report.logic.model_dump_json()
        db_review.style_review = final_report.style.model_dump_json()
        
        db_review.final_report = final_report.model_dump_json()
        db_review.overall_score = final_report.overall_score
        db_review.status = "completed"
        
        db.commit()

    except Exception as e:
        # 5. Handle failure
        db.rollback()
        db_review = db.query(Review).filter(Review.id == review_id).first()
        if db_review:
            db_review.status = "failed"
            db_review.error_message = str(e)
            db.commit()



# Code Review Endpoint
@router.post("/")
async def request_review(
    background_tasks: BackgroundTasks, 
    file: UploadFile = File(...),
    language: str = Form(...),
    user_id: int = Form(...),
    db: Session = Depends(get_db)
):

    # 1. Read file content
    try:
        content = await file.read()
        code_text = content.decode("utf-8")
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Could not read file: {str(e)}")

    # 2. Verify if user exists
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="User not found")

    # 3. Create 'pending' review row
    db_review = Review(
        user_id=user_id,
        code=code_text,
        language=language,
        status="pending"
    )
    db.add(db_review)
    db.commit()
    db.refresh(db_review)

    # 4. Fire background task
    background_tasks.add_task(process_review_background, db_review.id, db)

    # 5. Return review id and status
    return {
        "review_id": db_review.id,
        "status": "pending",
        "message": "Review started in background"
    }


# Get Review Status Endpoint
@router.get("/{review_id}", response_model=ReviewDetail)
def get_review_status(review_id: int, db: Session = Depends(get_db)):
    
    db_review = db.query(Review).filter(Review.id == review_id).first()
    
    if not db_review:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Review not found")

    return db_review

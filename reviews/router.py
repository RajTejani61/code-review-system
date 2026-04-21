from fastapi import APIRouter, Depends, BackgroundTasks, HTTPException, status, UploadFile, File, Form
from sqlalchemy.orm import Session

from database.database import get_db, SessionLocal
from agents.orchestrator_agent import run_review
from users.models import User
from reviews.models import Review
from reviews.schemas import ReviewDetail, ReviewSummary
from auth.oauth2 import get_current_user

router = APIRouter(
    prefix="/review",
    tags=["Reviews"]
)


# Background Task — creates its own DB session
async def process_review_background(review_id: int):
    """Runs the full agent review in the background and updates the DB.
    
    Opens a fresh session because the request-scoped session is already
    closed by the time FastAPI runs background tasks.
    """
    db: Session = SessionLocal()
    try:
        # 1. Fetch the review row
        db_review = db.query(Review).filter(Review.id == review_id).first()
        if not db_review:
            return

        # 2. Update status to 'processing'
        db_review.status = "processing"
        db.commit()

        # 3. Run the orchestrator agent
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
        # 5. Rollback and mark as failed
        db.rollback()
        db_review = db.query(Review).filter(Review.id == review_id).first()
        if db_review:
            db_review.status = "failed"
            db_review.error_message = str(e)
            db.commit()

    finally:
        # Close the session
        db.close()


# Submit Code Review
@router.post("/", status_code=status.HTTP_202_ACCEPTED)
async def request_review(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    language: str = Form(...),
    current_user: User = Depends(get_current_user), 
    db: Session = Depends(get_db)
):

    # 1. Read file content
    try:
        content = await file.read()
        code_text = content.decode("utf-8")
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Could not read file: {str(e)}")

    # 2. Change status
    db_review = Review(
        user_id=current_user.id,
        code=code_text,
        language=language,
        status="pending"
    )
    db.add(db_review)
    db.commit()
    db.refresh(db_review)

    # 3. Run Background task
    background_tasks.add_task(process_review_background, db_review.id)

    # 4. Return review id
    return {
        "review_id": db_review.id,
        "status": "pending",
        "message": "Review started"
    }



# Get Review Status
@router.get("/{review_id}", response_model=ReviewDetail)
def get_review_status(
    review_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    db_review = db.query(Review).filter(Review.id == review_id).first()

    if not db_review:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Review not found")

    if db_review.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorised to view this review")

    return db_review


# Get All User Reviews
@router.get("/", response_model=list[ReviewSummary])
def get_all_user_reviews(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Returns a summary list of all reviews belonging to the current user."""
    
    reviews = db.query(Review).filter(Review.user_id == current_user.id).order_by(Review.created_at.desc()).all()
    return reviews

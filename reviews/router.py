import json
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from database.database import get_db, SessionLocal
from agents.orchestrator_agent import orchestrator_graph
from users.models import User
from reviews.models import Review
from reviews.schemas import ReviewDetail, ReviewSummary
from auth.oauth2 import get_current_user

router = APIRouter(
    prefix="/review",
    tags=["Reviews"]
)


# Submit Code Review
@router.post("/", status_code=status.HTTP_201_CREATED)
async def request_review(
    file: UploadFile = File(...),
    language: str = Form(...),
    current_user: User = Depends(get_current_user), 
    db: Session = Depends(get_db)
):
    """Submits code for review and returns the review_id.
    
    The actual review process is triggered by connecting to the 
    GET /review/{review_id}/stream endpoint.
    """
    # 1. Read file content
    try:
        content = await file.read()
        code_text = content.decode("utf-8")
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Could not read file: {str(e)}")

    # 2. Save review record as pending
    db_review = Review(
        user_id=current_user.id,
        code=code_text,
        language=language,
        status="pending"
    )
    db.add(db_review)
    db.commit()
    db.refresh(db_review)

    # 3. Return review id
    return {
        "review_id": db_review.id,
        "status": "pending",
        "message": "Review submitted successfully."
    }


# SSE Streaming Endpoint
@router.get("/{review_id}/stream")
async def stream_review(
    review_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Streams the progress of a code review"""
    
    # 1. Fetch the review and verify ownership
    db_review = db.query(Review).filter(Review.id == review_id).first()
    if not db_review:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Review not found")
    
    if db_review.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorised to view this review")

    async def event_generator():
        # We open a fresh DB session for the generator because it runs in a different context
        gen_db: Session = SessionLocal()
        try:
            # Re-fetch the review in the new session
            review = gen_db.query(Review).filter(Review.id == review_id).first()
            
            # If already completed, just send the final report and close
            if review.status == "completed":
                yield f"data: {json.dumps({'event': 'report_done', 'data': json.loads(review.final_report)})}\n\n"
                return

            # Update status to processing
            review.status = "processing"
            gen_db.commit()

            inputs = {"code": review.code, "language": review.language, "messages": []}
            
            # Run LangGraph streaming
            async for event in orchestrator_graph.astream(inputs, stream_mode="updates"):
                for node_name, output in event.items():
                    payload = None
                    
                    if node_name == "security_node":
                        res = output.get("security_review")
                        review.security_review = res.model_dump_json()
                        payload = {"event": "security_done", "data": res.model_dump()}
                    
                    elif node_name == "performance_node":
                        res = output.get("performance_review")
                        review.performance_review = res.model_dump_json()
                        payload = {"event": "performance_done", "data": res.model_dump()}
                    
                    elif node_name == "logic_node":
                        res = output.get("logic_review")
                        review.logic_review = res.model_dump_json()
                        payload = {"event": "logic_done", "data": res.model_dump()}
                    
                    elif node_name == "style_node":
                        res = output.get("style_review")
                        review.style_review = res.model_dump_json()
                        payload = {"event": "style_done", "data": res.model_dump()}
                    
                    elif node_name == "generate_final_report":
                        res = output.get("final_report")
                        review.final_report = res.model_dump_json()
                        review.overall_score = res.overall_score
                        review.status = "completed"
                        payload = {"event": "report_done", "data": res.model_dump()}
                    
                    if payload:
                        gen_db.commit()
                        yield f"data: {json.dumps(payload)}\n\n"

        except Exception as e:
            gen_db.rollback()
            # Mark as failed in DB
            review = gen_db.query(Review).filter(Review.id == review_id).first()
            if review:
                review.status = "failed"
                review.error_message = str(e)
                gen_db.commit()
            yield f"data: {json.dumps({'event': 'error', 'data': str(e)})}\n\n"
        finally:
            gen_db.close()

    return StreamingResponse(event_generator(), media_type="text/event-stream")


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

from fastapi import FastAPI, File, UploadFile, Form, HTTPException, Depends, Request, Query
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from typing import Optional, List
import os
import uuid
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure embeddings before importing crewai
os.environ["TOKENIZERS_PARALLELISM"] = "false"  # Avoid tokenizer warnings

# Import and configure embeddings
import embeddings_config

from crewai import Crew, Process
from agents import financial_analyst
from task import analyze_financial_document_task

# Import database and Celery
from database import get_db, AnalysisRequest, AnalysisResult, UserActivity, init_db

# Initialize database
init_db()

# Try to import Celery (optional for backward compatibility)
try:
    from celery_worker import analyze_financial_document_task_celery
    CELERY_ENABLED = True
    print("✓ Celery integration enabled")
except ImportError:
    CELERY_ENABLED = False
    print("⚠ Celery not available - async processing disabled")

app = FastAPI(
    title="Financial Document Analyzer",
    description="AI-powered financial document analysis with queue-based processing and database storage",
    version="2.0.0"
)

def run_crew(query: str, file_path: str = "data/sample.pdf"):
    """Run the financial analysis crew with the given query and file path."""
    financial_crew = Crew(
        agents=[financial_analyst],
        tasks=[analyze_financial_document_task],
        process=Process.sequential,
    )
    
    # Pass both query and file_path to the crew
    result = financial_crew.kickoff(inputs={'query': query, 'file_path': file_path})
    
    # Handle both string and object results from CrewAI
    if isinstance(result, str):
        return result
    elif hasattr(result, 'raw'):
        return result.raw
    elif hasattr(result, 'output'):
        return result.output
    else:
        return str(result)

@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "message": "Financial Document Analyzer API is running",
        "version": "2.0.0",
        "features": {
            "async_processing": CELERY_ENABLED,
            "database": True,
            "sync_processing": True
        }
    }

@app.post("/analyze")
async def analyze_document(
    file: UploadFile = File(...),
    query: str = Form(default="Analyze this financial document for investment insights")
):
    """
    [SYNCHRONOUS] Analyze financial document and provide comprehensive investment recommendations.
    This endpoint blocks until analysis is complete. For async processing, use /analyze/async instead.
    """
    
    file_id = str(uuid.uuid4())
    file_path = f"data/financial_document_{file_id}.pdf"
    
    try:
        # Ensure data directory exists
        os.makedirs("data", exist_ok=True)
        
        # Save uploaded file
        with open(file_path, "wb") as f:
            content = await file.read()
            f.write(content)
        
        # Validate query
        if query == "" or query is None:
            query = "Analyze this financial document for investment insights"
            
        # Process the financial document with all analysts
        response = run_crew(query=query.strip(), file_path=file_path)
        
        return {
            "status": "success",
            "query": query,
            "analysis": response if isinstance(response, str) else str(response),
            "file_processed": file.filename
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing financial document: {str(e)}")
    
    finally:
        # Clean up uploaded file
        if os.path.exists(file_path):
            try:
                os.remove(file_path)
            except:
                pass  # Ignore cleanup errors


@app.post("/analyze/async")
async def analyze_document_async(
    request: Request,
    file: UploadFile = File(...),
    query: str = Form(default="Analyze this financial document for investment insights"),
    db: Session = Depends(get_db)
):
    """
    [ASYNCHRONOUS] Submit a financial document for analysis using queue-based processing.
    Returns immediately with a job_id that can be used to check status and retrieve results.
    
    Requires: Redis and Celery worker running
    """
    if not CELERY_ENABLED:
        raise HTTPException(
            status_code=503, 
            detail="Async processing not available. Redis/Celery not configured. Use /analyze endpoint instead."
        )
    
    job_id = str(uuid.uuid4())
    file_path = f"data/financial_document_{job_id}.pdf"
    
    try:
        # Ensure data directory exists
        os.makedirs("data", exist_ok=True)
        
        # Save uploaded file
        content = await file.read()
        file_size = len(content)
        
        with open(file_path, "wb") as f:
            f.write(content)
        
        # Validate query
        if query == "" or query is None:
            query = "Analyze this financial document for investment insights"
        
        # Get client IP
        client_ip = request.client.host if request.client else None
        
        # Create database record
        db_request = AnalysisRequest(
            job_id=job_id,
            filename=file.filename,
            query=query,
            status="pending"
        )
        db.add(db_request)
        db.commit()
        
        # Submit task to Celery
        analyze_financial_document_task_celery.delay(
            job_id=job_id,
            file_path=file_path,
            query=query.strip(),
            filename=file.filename,
            user_ip=client_ip,
            file_size=file_size
        )
        
        return {
            "status": "submitted",
            "job_id": job_id,
            "message": "Document submitted for analysis. Use /status/{job_id} to check progress.",
            "filename": file.filename,
            "query": query
        }
        
    except Exception as e:
        # Clean up on error
        if os.path.exists(file_path):
            try:
                os.remove(file_path)
            except:
                pass
        raise HTTPException(status_code=500, detail=f"Error submitting document for analysis: {str(e)}")


@app.get("/status/{job_id}")
async def get_job_status(job_id: str, db: Session = Depends(get_db)):
    """
    Check the status of an analysis job.
    
    Status values:
    - pending: Job submitted, waiting to be processed
    - processing: Job is currently being analyzed
    - completed: Analysis finished successfully
    - failed: Analysis failed with an error
    """
    db_request = db.query(AnalysisRequest).filter(AnalysisRequest.job_id == job_id).first()
    
    if not db_request:
        raise HTTPException(status_code=404, detail="Job not found")
    
    response = {
        "job_id": job_id,
        "status": db_request.status,
        "filename": db_request.filename,
        "query": db_request.query,
        "created_at": db_request.created_at.isoformat(),
        "updated_at": db_request.updated_at.isoformat()
    }
    
    if db_request.status == "completed":
        response["completed_at"] = db_request.completed_at.isoformat() if db_request.completed_at else None
        response["message"] = "Analysis completed. Use /result/{job_id} to retrieve the result."
    elif db_request.status == "failed":
        response["error"] = db_request.error_message
        response["completed_at"] = db_request.completed_at.isoformat() if db_request.completed_at else None
    
    return response


@app.get("/result/{job_id}")
async def get_job_result(job_id: str, db: Session = Depends(get_db)):
    """
    Retrieve the analysis result for a completed job.
    """
    db_result = db.query(AnalysisResult).filter(AnalysisResult.job_id == job_id).first()
    
    if not db_result:
        # Check if job exists but not completed
        db_request = db.query(AnalysisRequest).filter(AnalysisRequest.job_id == job_id).first()
        if db_request:
            if db_request.status == "pending" or db_request.status == "processing":
                raise HTTPException(
                    status_code=202, 
                    detail=f"Analysis not yet complete. Current status: {db_request.status}"
                )
            elif db_request.status == "failed":
                raise HTTPException(
                    status_code=500, 
                    detail=f"Analysis failed: {db_request.error_message}"
                )
        raise HTTPException(status_code=404, detail="Result not found")
    
    return {
        "status": "success",
        "job_id": job_id,
        "filename": db_result.filename,
        "query": db_result.query,
        "analysis": db_result.analysis,
        "processing_time": db_result.processing_time,
        "created_at": db_result.created_at.isoformat()
    }


@app.get("/history")
async def get_analysis_history(
    limit: int = Query(default=10, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    db: Session = Depends(get_db)
):
    """
    Retrieve analysis history with pagination.
    
    Parameters:
    - limit: Number of records to return (1-100, default: 10)
    - offset: Number of records to skip (default: 0)
    """
    total = db.query(AnalysisResult).count()
    results = db.query(AnalysisResult)\
        .order_by(AnalysisResult.created_at.desc())\
        .limit(limit)\
        .offset(offset)\
        .all()
    
    return {
        "total": total,
        "limit": limit,
        "offset": offset,
        "results": [
            {
                "job_id": r.job_id,
                "filename": r.filename,
                "query": r.query,
                "processing_time": r.processing_time,
                "created_at": r.created_at.isoformat()
            }
            for r in results
        ]
    }


@app.get("/stats")
async def get_statistics(db: Session = Depends(get_db)):
    """
    Get usage statistics and analytics.
    """
    total_analyses = db.query(AnalysisResult).count()
    total_requests = db.query(AnalysisRequest).count()
    
    pending = db.query(AnalysisRequest).filter(AnalysisRequest.status == "pending").count()
    processing = db.query(AnalysisRequest).filter(AnalysisRequest.status == "processing").count()
    completed = db.query(AnalysisRequest).filter(AnalysisRequest.status == "completed").count()
    failed = db.query(AnalysisRequest).filter(AnalysisRequest.status == "failed").count()
    
    # Calculate average processing time
    from sqlalchemy import func
    avg_time = db.query(func.avg(AnalysisResult.processing_time)).scalar()
    
    # Get success rate
    total_activity = db.query(UserActivity).count()
    successful_activity = db.query(UserActivity).filter(UserActivity.success == True).count()
    success_rate = (successful_activity / total_activity * 100) if total_activity > 0 else 0
    
    return {
        "total_analyses_completed": total_analyses,
        "total_requests": total_requests,
        "status_breakdown": {
            "pending": pending,
            "processing": processing,
            "completed": completed,
            "failed": failed
        },
        "average_processing_time_seconds": round(avg_time, 2) if avg_time else None,
        "success_rate_percentage": round(success_rate, 2),
        "celery_enabled": CELERY_ENABLED
    }

if __name__ == "__main__":
    import uvicorn
    # Use import string format for reload to work properly
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
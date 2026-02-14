"""
Celery worker tasks for asynchronous financial document analysis
"""
import os
import time
from datetime import datetime
from celery_config import celery_app
from dotenv import load_dotenv

load_dotenv()

# Configure embeddings before importing crewai
os.environ["TOKENIZERS_PARALLELISM"] = "false"

import embeddings_config
from crewai import Crew, Process
from agents import financial_analyst
from task import analyze_financial_document_task
from database import SessionLocal, AnalysisRequest, AnalysisResult, UserActivity


@celery_app.task(bind=True, name="analyze_financial_document")
def analyze_financial_document_task_celery(self, job_id: str, file_path: str, query: str, filename: str, user_ip: str = None, file_size: int = None):
    """
    Celery task for analyzing financial documents asynchronously
    
    Args:
        job_id: Unique job identifier
        file_path: Path to the uploaded PDF file
        query: Analysis query from user
        filename: Original filename
        user_ip: User's IP address (optional)
        file_size: File size in bytes (optional)
    """
    db = SessionLocal()
    start_time = time.time()
    
    try:
        # Update status to processing
        db_request = db.query(AnalysisRequest).filter(AnalysisRequest.job_id == job_id).first()
        if db_request:
            db_request.status = "processing"
            db_request.updated_at = datetime.utcnow()
            db.commit()
        
        # Update task state
        self.update_state(state='PROCESSING', meta={'status': 'Analyzing document...'})
        
        # Run the financial analysis crew
        financial_crew = Crew(
            agents=[financial_analyst],
            tasks=[analyze_financial_document_task],
            process=Process.sequential,
        )
        
        result = financial_crew.kickoff(inputs={'query': query, 'file_path': file_path})
        
        # Extract result text
        if isinstance(result, str):
            analysis_text = result
        elif hasattr(result, 'raw'):
            analysis_text = result.raw
        elif hasattr(result, 'output'):
            analysis_text = result.output
        else:
            analysis_text = str(result)
        
        processing_time = time.time() - start_time
        
        # Store result in database
        db_result = AnalysisResult(
            job_id=job_id,
            filename=filename,
            query=query,
            analysis=analysis_text,
            processing_time=processing_time
        )
        db.add(db_result)
        
        # Update request status
        if db_request:
            db_request.status = "completed"
            db_request.completed_at = datetime.utcnow()
            db_request.updated_at = datetime.utcnow()
        
        # Log user activity
        activity = UserActivity(
            job_id=job_id,
            user_ip=user_ip,
            file_size=file_size,
            query_length=len(query),
            success=True
        )
        db.add(activity)
        
        db.commit()
        
        # Clean up file
        if os.path.exists(file_path):
            try:
                os.remove(file_path)
            except:
                pass
        
        return {
            "status": "completed",
            "job_id": job_id,
            "analysis": analysis_text,
            "processing_time": processing_time,
            "filename": filename
        }
        
    except Exception as e:
        processing_time = time.time() - start_time
        error_message = str(e)
        
        # Update request status to failed
        db_request = db.query(AnalysisRequest).filter(AnalysisRequest.job_id == job_id).first()
        if db_request:
            db_request.status = "failed"
            db_request.error_message = error_message
            db_request.updated_at = datetime.utcnow()
            db_request.completed_at = datetime.utcnow()
        
        # Log failed activity
        activity = UserActivity(
            job_id=job_id,
            user_ip=user_ip,
            file_size=file_size,
            query_length=len(query) if query else 0,
            success=False
        )
        db.add(activity)
        
        db.commit()
        
        # Clean up file
        if file_path and os.path.exists(file_path):
            try:
                os.remove(file_path)
            except:
                pass
        
        # Re-raise exception for Celery to handle
        raise
        
    finally:
        db.close()

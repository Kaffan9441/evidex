from fastapi import APIRouter, UploadFile, File, HTTPException, Depends, BackgroundTasks
from typing import List
from sqlmodel import Session, select
from ..database import engine
from ..models import Document, DocumentResponse, TaskRequest, TaskResponse, TaskResult
from ..services.ocr import process_document
from ..services.llm import run_legal_task
import json
from datetime import datetime

router = APIRouter()

def get_session():
    with Session(engine) as session:
        yield session

@router.post("/upload", response_model=DocumentResponse)
async def upload_document(file: UploadFile = File(...), session: Session = Depends(get_session)):
    try:
        # Run OCR
        normalized_doc = await process_document(file)
        
        # Save to DB
        doc_model = Document(
            filename=normalized_doc["filename"],
            mime_type=normalized_doc["mime_type"],
            page_count=normalized_doc["page_count"],
            normalized_content_json=json.dumps(normalized_doc)
        )
        session.add(doc_model)
        session.commit()
        session.refresh(doc_model)
        
        return DocumentResponse(
            id=doc_model.id,
            filename=doc_model.filename,
            mime_type=doc_model.mime_type,
            page_count=doc_model.page_count,
            upload_timestamp=doc_model.upload_timestamp
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/docs", response_model=List[DocumentResponse])
def list_documents(session: Session = Depends(get_session)):
    docs = session.exec(select(Document).order_by(Document.upload_timestamp.desc())).all()
    return docs

async def process_task_background(task_id: int, task_type: str, doc_ids: List[int], instructions: str, jurisdiction: str):
    # Re-create session for background task
    with Session(engine) as session:
        task = session.get(TaskResult, task_id)
        if not task:
            return

        try:
            # Fetch docs
            docs_data = []
            for doc_id in doc_ids:
                doc = session.get(Document, doc_id)
                if doc:
                    docs_data.append(json.loads(doc.normalized_content_json))
            
            # Run LLM
            result = await run_legal_task(task_type, docs_data, instructions, jurisdiction)
            
            # Update Task
            task.status = "completed"
            task.completed_at = datetime.utcnow()
            task.result_json = json.dumps(result)
            session.add(task)
            session.commit()
            
        except Exception as e:
            task.status = "failed"
            task.error_message = str(e)
            session.add(task)
            session.commit()

@router.post("/run_task", response_model=TaskResponse)
async def run_task(request: TaskRequest, background_tasks: BackgroundTasks, session: Session = Depends(get_session)):
    # Create Task Record
    task = TaskResult(
        task_type=request.task_type,
        status="pending",
        document_ids_json=json.dumps(request.document_ids)
    )
    session.add(task)
    session.commit()
    session.refresh(task)
    
    # Trigger Background Task
    background_tasks.add_task(
        process_task_background, 
        task.id, 
        request.task_type, 
        request.document_ids, 
        request.instructions, 
        request.jurisdiction
    )
    
    return TaskResponse(
        id=task.id,
        task_type=task.task_type,
        status=task.status,
        created_at=task.created_at
    )

@router.get("/tasks/{task_id}", response_model=TaskResponse)
def get_task(task_id: int, session: Session = Depends(get_session)):
    task = session.get(TaskResult, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    result_dict = None
    if task.result_json:
        result_dict = json.loads(task.result_json)
        
    return TaskResponse(
        id=task.id,
        task_type=task.task_type,
        status=task.status,
        created_at=task.created_at,
        result=result_dict,
        error=task.error_message
    )

@router.get("/tasks", response_model=List[TaskResponse])
def list_tasks(session: Session = Depends(get_session)):
    tasks = session.exec(select(TaskResult).order_by(TaskResult.created_at.desc())).all()
    return [
        TaskResponse(
            id=t.id,
            task_type=t.task_type,
            status=t.status,
            created_at=t.created_at,
            result=json.loads(t.result_json) if t.result_json else None,
            error=t.error_message
        ) for t in tasks
    ]

from typing import List
from fastapi import APIRouter, Depends, HTTPException, status, Query
from app.models.document import Document, DocumentCreate, DocumentUpdate
from app.models.user import User
from app.services.document_service import document_service
from app.dependencies import get_current_active_user

router = APIRouter(prefix="/documents", tags=["documents"])

@router.post("/", response_model=Document)
async def create_document(
    document: DocumentCreate,
    current_user: User = Depends(get_current_active_user)
):
    """Create a new document"""
    return await document_service.create_document(document, current_user.id)

@router.get("/", response_model=List[Document])
async def get_documents(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    current_user: User = Depends(get_current_active_user)
):
    """Get all documents for the current user"""
    return await document_service.get_user_documents(current_user.id, skip, limit)

@router.get("/search", response_model=List[Document])
async def search_documents(
    q: str = Query(..., min_length=1),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    current_user: User = Depends(get_current_active_user)
):
    """Search documents"""
    return await document_service.search_documents(current_user.id, q, skip, limit)

@router.get("/{document_id}", response_model=Document)
async def get_document(
    document_id: str,
    current_user: User = Depends(get_current_active_user)
):
    """Get a specific document"""
    document = await document_service.get_document(document_id, current_user.id)
    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found"
        )
    return document

@router.put("/{document_id}", response_model=Document)
async def update_document(
    document_id: str,
    document_update: DocumentUpdate,
    current_user: User = Depends(get_current_active_user)
):
    """Update a document"""
    document = await document_service.update_document(document_id, document_update, current_user.id)
    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found"
        )
    return document

@router.delete("/{document_id}")
async def delete_document(
    document_id: str,
    current_user: User = Depends(get_current_active_user)
):
    """Delete a document"""
    success = await document_service.delete_document(document_id, current_user.id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found"
        )
    return {"message": "Document deleted successfully"}

@router.post("/{document_id}/duplicate", response_model=Document)
async def duplicate_document(
    document_id: str,
    current_user: User = Depends(get_current_active_user)
):
    """Duplicate a document"""
    document = await document_service.duplicate_document(document_id, current_user.id)
    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found"
        )
    return document
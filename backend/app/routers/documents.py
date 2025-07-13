from fastapi import APIRouter, Depends, HTTPException, status
from app.models.document import Document, DocumentCreate
from app.services import document_service as ds_module
from app.dependencies import get_current_user
from app.models.user import User

router = APIRouter()

@router.post("/", response_model=Document)
async def create_document(document: DocumentCreate, current_user: User = Depends(get_current_user)):
    if not ds_module.document_service:
        raise HTTPException(status_code=500, detail="DocumentService not initialized")
    return await ds_module.document_service.create_document(document, current_user.id)

@router.get("/documents/", response_model=list[Document])
async def get_my_documents(current_user: User = Depends(get_current_user)):
    return await ds_module.document_service.get_documents_by_user(current_user.id)

@router.get("/documents/{doc_id}", response_model=Document)
async def get_document(doc_id: str, current_user: User = Depends(get_current_user)):
    doc = await ds_module.document_service.get_document(doc_id)
    if not doc or doc.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Document not found")
    return doc

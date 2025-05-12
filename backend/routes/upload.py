
from fastapi import APIRouter, UploadFile, File, HTTPException
import uuid
import os
from services.file_handler import save_upload_file
from models.schema import UploadResponse

router = APIRouter()

@router.post("/upload", response_model=UploadResponse)
async def upload_file(file: UploadFile = File(...)):
    """
    Upload a PDF or image file and save it to the uploads directory.
    Returns the filename and path to access the file.
    """
    # Check file type
    allowed_types = ["application/pdf", "image/png", "image/jpeg", "image/jpg"]
    content_type = file.content_type or ""
    
    if content_type not in allowed_types:
        raise HTTPException(
            status_code=400, 
            detail=f"File type not allowed. Must be one of: {', '.join(allowed_types)}"
        )
    
    # Generate unique filename
    original_filename = file.filename or "unnamed_file"
    file_extension = original_filename.split(".")[-1]
    unique_filename = f"{uuid.uuid4()}.{file_extension}"
    
    # Save file
    file_path = await save_upload_file(file, unique_filename)
    
    # Generate URL path (relative to the server)
    relative_path = f"/uploads/{unique_filename}"
    
    return UploadResponse(
        filename=unique_filename,
        path=relative_path
    )

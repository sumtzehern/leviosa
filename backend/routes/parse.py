
from fastapi import APIRouter, UploadFile, File, HTTPException, Form, Body
from typing import Optional
import os
from services.ocr_easyocr import extract_text_and_boxes
from models.schema import OCRResponse, OCRRequest
from services.pdf_converter import convert_pdf_to_images

router = APIRouter()

@router.post("/ocr", response_model=OCRResponse)
async def ocr_extract(
    file: Optional[UploadFile] = File(None),
    request: Optional[OCRRequest] = None
):
    """
    Extract text and bounding boxes from an image using EasyOCR.
    Accepts either:
    - A directly uploaded file
    - A JSON body with a path to a previously uploaded file
    """
    # Handle file upload case
    if file:
        # Check file type
        allowed_types = ["image/png", "image/jpeg", "image/jpg"]
        content_type = file.content_type or ""
        
        if content_type not in allowed_types:
            raise HTTPException(
                status_code=400, 
                detail=f"File type not allowed for OCR. Must be one of: {', '.join(allowed_types)}"
            )
        
        # Process the file directly
        result = await extract_text_and_boxes(file)
        return result
    
    # Handle JSON request with path
    elif request and request.path:
        # Construct the full path to the file
        filename = os.path.basename(request.path)
        full_path = os.path.join("uploads", filename)
        
        if not os.path.exists(full_path):
            raise HTTPException(
                status_code=404,
                detail=f"File not found: {filename}"
            )
        
        # Process the file from path
        # convert pdf to images
        if filename.endswith(".pdf"):
            image_paths = convert_pdf_to_images(full_path)
            result = []
            for i, image_path in enumerate(image_paths):
                ocr_result = await extract_text_and_boxes(image_paths)
                result.append({
                    "page": i + 1,
                    "results": ocr_result.results, # assume results is a field in the OCRResponse
                })
                return {"pages": result}
            else:
                result = await extract_text_and_boxes(full_path)
                return { "pages": [{ "page": 1, "results": result.results }] }
        else:
            result = await extract_text_and_boxes(full_path)
            return { "pages": [{ "page": 1, "results": result.results }] }
    
    # Neither file nor path provided
    else:
        raise HTTPException(
            status_code=400,
            detail="Either file upload or JSON path must be provided"
        )

# Alternative endpoint that accepts form data with file path
@router.post("/ocr/path", response_model=OCRResponse)
async def ocr_extract_path(
    path: str = Form(...)
):
    """
    Extract text and bounding boxes using a path to an existing file.
    """
    # Construct the full path to the file
    filename = os.path.basename(path)
    full_path = os.path.join("uploads", filename)
    
    if not os.path.exists(full_path):
        raise HTTPException(
            status_code=404,
            detail=f"File not found: {filename}"
        )
    
    # Process the file
    result = await extract_text_and_boxes(full_path)
    return result

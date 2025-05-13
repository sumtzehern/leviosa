import traceback
from fastapi import APIRouter, UploadFile, File, HTTPException
from models.schema import OCRResponse, OCRRequest, MarkdownRequest, MarkdownResponse
from services.ocr_paddleocr import extract_text_and_boxes
from services.pdf_converter import convert_pdf_to_images
from services.markdown_processor import MarkdownProcessor
import os

router = APIRouter()
markdown_processor = MarkdownProcessor()


# Upload File → OCR directly
@router.post("/ocr/file", response_model=OCRResponse)
async def ocr_from_upload(file: UploadFile = File(...)):
    """
    Upload and OCR a single image file.
    Supports PNG, JPG, JPEG.
    """
    allowed_types = ["image/png", "image/jpeg", "image/jpg", "application/pdf"]
    content_type = file.content_type or ""
    
    if content_type not in allowed_types:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid file type. Supported: {', '.join(allowed_types)}"
        )

    return await extract_text_and_boxes(file)


# OCR from saved file path (e.g., after /upload)
@router.post("/ocr/path", response_model=OCRResponse)
async def ocr_from_path(request: OCRRequest):
    """
    Perform OCR using a path to a previously uploaded file.
    Supports PDFs (multi-page) and images.
    """
    try:
        filename = os.path.basename(request.path)
        full_path = os.path.join("uploads", filename)

        print(f"[OCR PATH] Attempting to read file at: {full_path}")

        if not os.path.exists(full_path):
            raise HTTPException(status_code=404, detail=f"File not found: {filename}")

        # Handle PDF (convert pages first)
        if filename.lower().endswith(".pdf"):
            image_paths = convert_pdf_to_images(full_path)
            results = []
            for i, image_path in enumerate(image_paths):
                page_result = await extract_text_and_boxes(image_path)
                results.append(page_result.pages[0])  # Assumes 1 page per image
            return OCRResponse(pages=results)

        # Image case
        return await extract_text_and_boxes(full_path)

    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


# Convert OCR results to Markdown
@router.post("/markdown", response_model=MarkdownResponse)
async def convert_to_markdown(request: MarkdownRequest):
    """
    Convert OCR results to Markdown format using LLM
    """
    try:
        # Process OCR results into markdown
        raw_text = markdown_processor.ocr_to_raw_text(request.ocr_response)
        markdown = markdown_processor.convert_to_markdown(request.ocr_response)
        
        return MarkdownResponse(
            markdown=markdown,
            raw_text=raw_text
        )
        
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

# One-step OCR and Markdown conversion from file
@router.post("/ocr-to-markdown", response_model=MarkdownResponse)
async def ocr_to_markdown(file: UploadFile = File(...)):
    """
    Upload, OCR, and convert to Markdown in one step
    """
    try:
        # First perform OCR
        ocr_response = await ocr_from_upload(file)
        
        # Then convert to markdown
        raw_text = markdown_processor.ocr_to_raw_text(ocr_response)
        markdown = markdown_processor.convert_to_markdown(ocr_response)
        
        return MarkdownResponse(
            markdown=markdown,
            raw_text=raw_text
        )
        
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))
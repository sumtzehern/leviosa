import traceback
from fastapi import APIRouter, UploadFile, File, HTTPException, WebSocket # type: ignore
from fastapi.responses import StreamingResponse
from models.schema import LayoutAnalysisResponse, OCRResponse, OCRRequest, MarkdownRequest, MarkdownResponse
from services.ocr_paddleocr import extract_text_and_boxes
from services.layout_analyzer import analyze_layout
from services.layout_postprocessor import LayoutPostprocessor
from services.pdf_to_image import convert_pdf_to_images
from services.markdown_processor import MarkdownProcessor
from services.markdown_refiner import MarkdownRefiner
import os
from typing import Dict, Any
import json
import asyncio

router = APIRouter()
markdown_processor = MarkdownProcessor()
layout_postprocessor = LayoutPostprocessor()
markdown_refiner = MarkdownRefiner()

# Layout analysis endpoint
@router.post("/layout", response_model=LayoutAnalysisResponse)
async def layout_from_upload(file: UploadFile = File(...)):
    """
    Upload and analyze layout of a document.
    Returns semantic regions with their types and locations.
    """
    allowed_types = ["image/png", "image/jpeg", "image/jpg", "application/pdf"]
    content_type = file.content_type or ""
    
    if content_type not in allowed_types:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid file type. Supported: {', '.join(allowed_types)}"
        )

    return await analyze_layout(file)

# Layout analysis from saved file
@router.post("/layout/path", response_model=LayoutAnalysisResponse)
async def layout_from_path(request: OCRRequest):
    """
    Perform layout analysis on a previously uploaded file.
    """
    try:
        filename = os.path.basename(request.path)
        full_path = os.path.join("uploads", filename)

        if not os.path.exists(full_path):
            raise HTTPException(status_code=404, detail=f"File not found: {filename}")

        return await analyze_layout(full_path)

    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

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

@router.post("/layout/enhanced", response_model=LayoutAnalysisResponse)
async def enhanced_layout_from_upload(file: UploadFile = File(...)):
    """
    Upload and analyze layout of a document with enhanced region classification.
    This endpoint applies advanced heuristics to better classify document regions.
    """
    allowed_types = ["image/png", "image/jpeg", "image/jpg", "application/pdf"]
    content_type = file.content_type or ""
    
    if content_type not in allowed_types:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid file type. Supported: {', '.join(allowed_types)}"
        )

    # First perform basic layout analysis
    layout_result = await analyze_layout(file)
    
    # Convert Pydantic models to dictionaries for postprocessing
    pages_dict = [page.dict() for page in layout_result.pages]
    
    # Apply enhancement
    enhanced_pages = layout_postprocessor.process_regions(pages_dict)
    
    # Return as Pydantic response model
    return LayoutAnalysisResponse(pages=enhanced_pages)

@router.post("/layout/path/enhanced", response_model=LayoutAnalysisResponse)
async def enhanced_layout_from_path(request: OCRRequest):
    """
    Perform enhanced layout analysis on a previously uploaded file.
    """
    try:
        filename = os.path.basename(request.path)
        full_path = os.path.join("uploads", filename)

        if not os.path.exists(full_path):
            raise HTTPException(status_code=404, detail=f"File not found: {filename}")

        # First perform basic layout analysis
        layout_result = await analyze_layout(full_path)
        
        # Then enhance region classifications
        enhanced_result = LayoutAnalysisResponse(
            pages=layout_postprocessor.process_regions(layout_result.pages)
        )
        
        return enhanced_result

    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/layout/enhanced/markdown", response_model=MarkdownResponse)
async def enhanced_layout_to_markdown(request: OCRRequest):
    """
    Convert layout-enhanced analysis results to markdown by processing all pages.
    This provides a complete markdown document for the entire file.
    """
    try:
        filename = os.path.basename(request.path)
        full_path = os.path.join("uploads", filename)

        if not os.path.exists(full_path):
            raise HTTPException(status_code=404, detail=f"File not found: {filename}")

        # Perform layout analysis with enhancement
        layout_result = await analyze_layout(full_path)
        
        # Convert Pydantic models to dictionaries for postprocessing
        pages_dict = [page.dict() for page in layout_result.pages]
        
        # Apply enhancement
        enhanced_pages = layout_postprocessor.process_regions(pages_dict)
        enhanced_result = LayoutAnalysisResponse(pages=enhanced_pages)
        
        # Convert to markdown using layout awareness
        markdown = await markdown_processor.layout_to_markdown(enhanced_result)
        
        # Get raw text for backward compatibility
        raw_text = ""
        for page in enhanced_result.pages:
            for region in page.results:
                if "text" in region.content:
                    raw_text += region.content["text"] + "\n"
        
        return MarkdownResponse(
            markdown=markdown,
            raw_text=raw_text
        )
        
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/layout/enhanced/markdown/stream")
async def stream_enhanced_layout_to_markdown(request: OCRRequest):
    """
    Stream layout-enhanced results to markdown page by page.
    Returns a streaming response with each page's markdown as it's processed.
    """
    try:
        filename = os.path.basename(request.path)
        full_path = os.path.join("uploads", filename)

        if not os.path.exists(full_path):
            raise HTTPException(status_code=404, detail=f"File not found: {filename}")

        # Perform layout analysis with enhancement
        layout_result = await analyze_layout(full_path)
        
        # Convert Pydantic models to dictionaries for postprocessing
        pages_dict = [page.dict() for page in layout_result.pages]
        
        # Apply enhancement
        enhanced_pages = layout_postprocessor.process_regions(pages_dict)
        enhanced_result = LayoutAnalysisResponse(pages=enhanced_pages)
        
        # Set up streaming response
        async def generate():
            async for page_result in markdown_processor.process_layout_incrementally(enhanced_result):
                yield json.dumps(page_result) + "\n"
                
        return StreamingResponse(generate(), media_type="application/x-ndjson")

    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@router.websocket("/ws/layout/markdown")
async def websocket_enhanced_layout_to_markdown(websocket: WebSocket):
    """
    WebSocket endpoint for real-time page-by-page markdown processing of layout-enhanced results.
    """
    await websocket.accept()
    
    try:
        # Receive file path from client
        data = await websocket.receive_json()
        file_path = data.get("path")
        
        if not file_path:
            await websocket.send_json({"error": "No file path provided"})
            return
            
        full_path = os.path.join("uploads", os.path.basename(file_path))
        
        if not os.path.exists(full_path):
            await websocket.send_json({"error": f"File not found: {file_path}"})
            return
            
        # Perform layout analysis with enhancement
        layout_result = await analyze_layout(full_path)
        pages_dict = [page.dict() for page in layout_result.pages]
        enhanced_pages = layout_postprocessor.process_regions(pages_dict)
        enhanced_result = LayoutAnalysisResponse(pages=enhanced_pages)
        
        # Process each page and send results in real-time
        async for page_result in markdown_processor.process_layout_incrementally(enhanced_result):
            await websocket.send_json(page_result)
            
        # Signal completion
        await websocket.send_json({"status": "complete"})
        
    except Exception as e:
        traceback.print_exc()
        await websocket.send_json({"error": str(e)})
    
    finally:
        await websocket.close()

@router.post("/layout/enhanced/markdown/direct", response_model=MarkdownResponse)
async def direct_layout_to_markdown(request: OCRRequest):
    """
    Convert layout-enhanced analysis results directly to markdown without additional processing.
    This endpoint sends the layout JSON directly to the OpenAI API using the existing markdown_conversion.txt prompt.
    """
    try:
        filename = os.path.basename(request.path)
        full_path = os.path.join("uploads", filename)

        if not os.path.exists(full_path):
            raise HTTPException(status_code=404, detail=f"File not found: {filename}")

        # Perform layout analysis with enhancement
        layout_result = await analyze_layout(full_path)
        
        # Convert Pydantic models to dictionaries for postprocessing
        pages_dict = [page.dict() for page in layout_result.pages]
        
        # Apply enhancement
        enhanced_pages = layout_postprocessor.process_regions(pages_dict)
        enhanced_result = LayoutAnalysisResponse(pages=enhanced_pages)
        
        # Convert enhanced result to dictionary for direct processing
        layout_json = enhanced_result.dict()
        
        # Convert to markdown directly using the existing prompt
        markdown = await markdown_processor.direct_layout_to_markdown(layout_json)
        
        # Get raw text for backward compatibility
        raw_text = ""
        for page in enhanced_result.pages:
            for region in page.results:
                if "text" in region.content:
                    raw_text += region.content["text"] + "\n"
        
        return MarkdownResponse(
            markdown=markdown,
            raw_text=raw_text
        )
        
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/layout/enhanced/markdown/direct/multipage", response_model=MarkdownResponse)
async def direct_multipage_layout_to_markdown(request: OCRRequest):
    """
    Convert layout-enhanced analysis results from all pages directly to markdown.
    This endpoint processes all pages in the document, not just the first one,
    and sends the complete layout JSON to the OpenAI API.
    """
    try:
        filename = os.path.basename(request.path)
        full_path = os.path.join("uploads", filename)

        if not os.path.exists(full_path):
            raise HTTPException(status_code=404, detail=f"File not found: {filename}")

        # Perform layout analysis with enhancement
        layout_result = await analyze_layout(full_path)
        
        # Convert Pydantic models to dictionaries for postprocessing
        pages_dict = [page.dict() for page in layout_result.pages]
        
        # Apply enhancement
        enhanced_pages = layout_postprocessor.process_regions(pages_dict)
        enhanced_result = LayoutAnalysisResponse(pages=enhanced_pages)
        
        # Process all pages, not just the first one
        markdown = await markdown_processor.convert_layout_json_to_markdown(enhanced_result)
        
        # Get raw text for backward compatibility
        raw_text = ""
        for page in enhanced_result.pages:
            for region in page.results:
                if "text" in region.content:
                    raw_text += region.content["text"] + "\n"
        
        return MarkdownResponse(
            markdown=markdown,
            raw_text=raw_text
        )
        
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/layout/enhanced/markdown/direct/multipage/refined", response_model=MarkdownResponse)
async def refined_multipage_layout_to_markdown(request: OCRRequest):
    """
    Process the document with a two-stage approach: 
    1. Convert layout-enhanced analysis from all pages to markdown
    2. Refine the markdown with an additional LLM pass for cleaner output
    
    This produces high-quality, display-ready markdown with consistent formatting.
    """
    try:
        filename = os.path.basename(request.path)
        full_path = os.path.join("uploads", filename)

        if not os.path.exists(full_path):
            raise HTTPException(status_code=404, detail=f"File not found: {filename}")

        # Perform layout analysis with enhancement
        layout_result = await analyze_layout(full_path)
        
        # Convert Pydantic models to dictionaries for postprocessing
        pages_dict = [page.dict() for page in layout_result.pages]
        
        # Apply enhancement
        enhanced_pages = layout_postprocessor.process_regions(pages_dict)
        enhanced_result = LayoutAnalysisResponse(pages=enhanced_pages)
        
        # Process all pages, not just the first one
        raw_markdown = await markdown_processor.convert_layout_json_to_markdown(enhanced_result)
        
        # Second pass: refine the markdown
        refined_markdown = markdown_refiner.refine_markdown(raw_markdown)
        
        # Get raw text for backward compatibility
        raw_text = ""
        for page in enhanced_result.pages:
            for region in page.results:
                if "text" in region.content:
                    raw_text += region.content["text"] + "\n"
        
        return MarkdownResponse(
            markdown=refined_markdown,
            raw_text=raw_text
        )
        
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))
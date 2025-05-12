
from pydantic import BaseModel
from typing import List, Optional, Union, Dict, Any

class UploadResponse(BaseModel):
    """Response model for file uploads"""
    filename: str
    path: str

class OCRRequest(BaseModel):
    """Request model for OCR processing using a file path"""
    path: str

class OCRResult(BaseModel):
    """Model for an individual OCR result"""
    text: str
    bbox: List[float]  # [x1, y1, x2, y2]
    confidence: float

class OCRResponse(BaseModel):
    """Response model for OCR processing"""
    results: List[OCRResult]

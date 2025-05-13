
from pydantic import BaseModel
from typing import List, Optional, Union, Dict, Any

class UploadResponse(BaseModel):
    """Response model for file uploads"""
    filename: str
    path: str

class OCRRequest(BaseModel):
    path: str

class OCRResult(BaseModel):
    text: str
    bbox: List[float]  # e.g., [x1, y1, x2, y2]
    confidence: float

class OCRPageResult(BaseModel):
    page: int
    results: List[OCRResult]

class OCRResponse(BaseModel):
    pages: List[OCRPageResult]


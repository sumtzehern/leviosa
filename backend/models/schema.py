
from pydantic import BaseModel
from typing import List, Optional, Union, Dict, Any

class UploadResponse(BaseModel):
    """Response model for file uploads"""
    filename: str
    path: str

class OCRRequest(BaseModel):
    path: str

class OCRResult(BaseModel):
    line_id: str
    text: str
    confidence: float
    bbox_raw: List[List[float]]
    bbox_norm: List[float]
    low_confidence: bool
    line_class: Optional[str]
    page: int


class OCRPageResult(BaseModel):
    page: int
    results: List[OCRResult]

class OCRResponse(BaseModel):
    pages: List[OCRPageResult]


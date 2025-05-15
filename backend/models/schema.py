from pydantic import BaseModel
from typing import List, Optional, Union, Dict, Any

class UploadResponse(BaseModel):
    """Response model for file uploads"""
    filename: str
    path: str

class LayoutResult(BaseModel):
    region_id: str
    region_type: str  # "text", "table", "figure", etc.
    bbox_raw: List[float]
    bbox_norm: List[float]
    content: Dict[str, Any]
    page: int

class LayoutPageResult(BaseModel):
    page: int
    results: List[LayoutResult]

class LayoutAnalysisResponse(BaseModel):
    pages: List[LayoutPageResult]

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

class MarkdownRequest(BaseModel):
    """Request model for markdown conversion"""
    ocr_response: OCRResponse

class MarkdownResponse(BaseModel):
    """Response model for markdown conversion"""
    markdown: str
    raw_text: str
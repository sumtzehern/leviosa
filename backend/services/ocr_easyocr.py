
import easyocr
import numpy as np
from PIL import Image
import io
import os
from typing import Union, List, Dict, Any, BinaryIO
from fastapi import UploadFile
from models.schema import OCRResponse, OCRResult

# Initialize the OCR reader (this is done once when the module is loaded)
# We're using English as the default language
reader = easyocr.Reader(['en'], gpu=False)

async def extract_text_and_boxes(
    input_file: Union[str, UploadFile, BinaryIO]
) -> OCRResponse:
    """
    Extract text and bounding boxes from an image using EasyOCR.
    
    Args:
        input_file: Either a path to an image file or an UploadFile object
        
    Returns:
        A dict containing the extracted text and bounding boxes
    """
    # Process the file based on its type
    if isinstance(input_file, str):
        # Input is a file path
        image = Image.open(input_file)
        image_np = np.array(image)
    else:
        # Input is an UploadFile or file-like object
        content = await input_file.read() if hasattr(input_file, "read") and callable(input_file.read) else input_file.read()
        image = Image.open(io.BytesIO(content))
        image_np = np.array(image)
        
        # Reset file pointer if it's an UploadFile
        if hasattr(input_file, "seek") and callable(input_file.seek):
            await input_file.seek(0)
    
    # Perform OCR
    results = reader.readtext(image_np)
    
    # Format the results
    ocr_results = []
    for bbox, text, confidence in results:
        # EasyOCR returns bbox as [[x1,y1],[x2,y1],[x2,y2],[x1,y2]]
        # We'll convert it to [x1,y1,x2,y2] format (top-left to bottom-right)
        x1, y1 = bbox[0]
        x2, y2 = bbox[2]
        
        ocr_results.append(OCRResult(
            text=text,
            bbox=[x1, y1, x2, y2],
            confidence=float(confidence)
        ))
    
    return OCRResponse(
        results=ocr_results
    )

import easyocr 
import numpy as np
from PIL import Image
import io
import os
import uuid
import re
from typing import Union, List, BinaryIO
from fastapi import UploadFile

from models.schema import OCRResponse, OCRResult, OCRPageResult
from services.pdf_converter import convert_pdf_to_images  # You already have this

reader = easyocr.Reader(['en'], gpu=False)


async def extract_text_and_boxes(
    input_file: Union[str, UploadFile, BinaryIO]
) -> OCRResponse:
    """
    Extract text and bounding boxes from image or PDF input.
    Supports:
    - PDF: auto converts to pages and tags per-page
    - Image: returns single page
    """
    # Case 1: PDF file
    if isinstance(input_file, str) and input_file.lower().endswith(".pdf"):
        image_paths = convert_pdf_to_images(input_file)
        pages = []
        for i, image_path in enumerate(image_paths):
            page_result = await _process_image_path(image_path, page=i + 1)
            pages.append(page_result)
        return OCRResponse(pages=pages)

    # Case 2: Image from file path
    if isinstance(input_file, str) and input_file.lower().endswith((".png", ".jpg", ".jpeg")):
        page_result = await _process_image_path(input_file, page=1)
        return OCRResponse(pages=[page_result])

    # Case 3: UploadFile or BinaryIO
    return OCRResponse(pages=[await _process_image_input(input_file, page=1)])


# OCR EasyOCR
async def _process_image_input(
    input_file: Union[UploadFile, BinaryIO], page: int
) -> OCRPageResult:
    content = await input_file.read() if hasattr(input_file, "read") else input_file.read()
    image = Image.open(io.BytesIO(content)).convert("RGB")
    if hasattr(input_file, "seek"):
        await input_file.seek(0)
    return _process_pil_image(image, page)


async def _process_image_path(
    path: str, page: int
) -> OCRPageResult:
    image = Image.open(path).convert("RGB")
    return _process_pil_image(image, page)


def _process_pil_image(image: Image.Image, page: int) -> OCRPageResult:
    width, height = image.size
    image_np = np.array(image)

    results = reader.readtext(image_np)
    blocks = []

    for bbox, text, confidence in results:
        x1, y1 = bbox[0]
        x2, y2 = bbox[2]
        norm_bbox = [
            round(x1 / width, 6),
            round(y1 / height, 6),
            round(x2 / width, 6),
            round(y2 / height, 6),
        ]
        clean_text = re.sub(r'\s+', ' ', text.strip())

        block = OCRResult(
            line_id=str(uuid.uuid4()),
            text=clean_text,
            confidence=round(confidence, 4),
            bbox_raw=bbox,
            bbox_norm=norm_bbox,
            low_confidence=confidence < 0.6,
            line_class=None,
            page=page
        )
        blocks.append((y1, block))

    blocks.sort(key=lambda b: b[0])
    return OCRPageResult(
        page=page,
        results=[b[1] for b in blocks]
    )

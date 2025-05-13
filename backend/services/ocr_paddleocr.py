import numpy as np
from PIL import Image
import io
import uuid
import re
from typing import Union, BinaryIO
from fastapi import UploadFile
import asyncio

from models.schema import OCRResponse, OCRResult, OCRPageResult
from services.pdf_converter import convert_pdf_to_images
from paddleocr import PaddleOCR

# Initialize PaddleOCR (lightweight EN version, CPU)
ocr_engine = PaddleOCR(
    use_angle_cls=True,
    lang='en',
    det_model_dir='models/en_PP-OCRv3_det_infer',
    rec_model_dir='models/en_PP-OCRv3_rec_infer',
    use_gpu=False
)

async def extract_text_and_boxes(
    input_file: Union[str, UploadFile, BinaryIO]
) -> OCRResponse:
    if isinstance(input_file, str) and input_file.lower().endswith(".pdf"):
        image_paths = convert_pdf_to_images(input_file)[:3]  # Limit to 3 pages
        pages = [await _process_image_path(p, i + 1) for i, p in enumerate(image_paths)]
        return OCRResponse(pages=pages)

    if isinstance(input_file, str) and input_file.lower().endswith((".png", ".jpg", ".jpeg")):
        return OCRResponse(pages=[await _process_image_path(input_file, page=1)])

    return OCRResponse(pages=[await _process_image_input(input_file, page=1)])

async def _process_image_input(input_file: Union[UploadFile, BinaryIO], page: int) -> OCRPageResult:
    content = await input_file.read() if hasattr(input_file, "read") else input_file.read()
    image = Image.open(io.BytesIO(content)).convert("RGB")
    if hasattr(input_file, "seek"):
        await input_file.seek(0)
    return await _process_pil_image(image, page)

async def _process_image_path(path: str, page: int) -> OCRPageResult:
    image = Image.open(path).convert("RGB")
    return await _process_pil_image(image, page)

async def _process_pil_image(image: Image.Image, page: int) -> OCRPageResult:
    width, height = image.size
    image_np = np.array(image)
    results = await asyncio.to_thread(ocr_engine.ocr, image_np, cls=True)

    blocks = []
    for line in results[0]:
        bbox, (text, confidence) = line
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
            low_confidence=confidence < 0.7,
            line_class=None,
            page=page
        )
        blocks.append((y1, block))

    blocks.sort(key=lambda b: b[0])
    return OCRPageResult(page=page, results=[b[1] for b in blocks])
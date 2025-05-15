# backend/services/layout_analyzer.py
import json
import os
import uuid
import numpy as np
from PIL import Image
from paddleocr import PPStructure, save_structure_res
from typing import Union, BinaryIO, Dict, List, Any
from fastapi import UploadFile
import asyncio
import io
from uuid import uuid4

from models.schema import LayoutAnalysisResponse, LayoutResult, LayoutPageResult

# Initialize PP-Structure layout analysis
structure_engine = PPStructure(
    table=True,
    ocr=True,
    layout=True, 
    show_log=True,
    recovery=False,
    use_pdf2docx_api=False,
    lang="en",
    layout_model_dir='models/layout_ppv3_infer',
    layout_dict_path='models/layout_dict.txt',
)

async def analyze_layout(
    input_file: Union[str, UploadFile, BinaryIO]
) -> LayoutAnalysisResponse:
    """
    Analyzes document layout to identify text regions, tables, and figures
    before performing OCR
    """
    if isinstance(input_file, str) and input_file.lower().endswith(".pdf"):
        from services.pdf_to_image import convert_pdf_to_images
        image_paths = convert_pdf_to_images(input_file)[:3]  # Limit to 3 pages
        pages = [await _process_layout_from_path(p, i + 1) for i, p in enumerate(image_paths)]
        return LayoutAnalysisResponse(pages=pages)

    if isinstance(input_file, str) and input_file.lower().endswith((".png", ".jpg", ".jpeg")):
        return LayoutAnalysisResponse(pages=[await _process_layout_from_path(input_file, page=1)])

    return LayoutAnalysisResponse(pages=[await _process_layout_from_input(input_file, page=1)])

async def _process_layout_from_input(input_file: Union[UploadFile, BinaryIO], page: int) -> LayoutPageResult:
    content = await input_file.read() if hasattr(input_file, "read") else input_file.read()
    image = Image.open(io.BytesIO(content)).convert("RGB")
    if hasattr(input_file, "seek"):
        await input_file.seek(0)
    return await _process_layout_from_image(image, page)

async def _process_layout_from_path(path: str, page: int) -> LayoutPageResult:
    image = Image.open(path).convert("RGB")
    return await _process_layout_from_image(image, page)

# async def _process_layout_from_image(image: Image.Image, page: int) -> LayoutPageResult:
#     width, height = image.size
#     image_np = np.array(image)
    
#     # Run layout analysis
#     result = await asyncio.to_thread(structure_engine, image_np)
    
#     # Debug print
#     print("LAYOUT ANALYSIS RESULT:")
#     import json
#     print(json.dumps(result, default=str, indent=2))
    
#     # Just create a simple result for testing
#     layout_results = []
    
#     for i, region in enumerate(result):
#         # Create a simple result with minimal processing
#         region_type = region.get("type", "unknown")
#         bbox = region.get("bbox", [0, 0, 0, 0])
        
#         # Skip the problematic code and just include the raw result
#         content = {
#             "raw_data": str(region.get("res", "No result data"))
#         }
        
#         layout_result = LayoutResult(
#             region_id=f"region_{i}",
#             region_type=region_type,
#             bbox_raw=bbox,
#             bbox_norm=bbox,  # Just use the same bbox for testing
#             content=content,
#             page=page
#         )
#         layout_results.append(layout_result)
    
#     return LayoutPageResult(page=page, results=layout_results)

async def _process_layout_from_image(image: Image.Image, page: int) -> LayoutPageResult:
    width, height = image.size
    image_np = np.array(image)
    
    # Run layout analysis
    result = await asyncio.to_thread(structure_engine, image_np)
    
    layout_results = []
    
    for i, region in enumerate(result):
        region_type = region.get("type", "unknown")
        bbox = region.get("bbox", [0, 0, 0, 0])
        
        # Normalize coordinates
        x1, y1, x2, y2 = bbox
        norm_bbox = [
            round(x1 / width, 6),
            round(y1 / height, 6),
            round(x2 / width, 6),
            round(y2 / height, 6),
        ]
        
        # Get the raw OCR results
        ocr_results = region.get("res", [])
        
        # Parse OCR results correctly based on their format
        if region_type == "table":
            # For tables, extract the HTML and cell data
            content = {
                "html": ocr_results.get("html", "") if isinstance(ocr_results, dict) else "",
                "cells": ocr_results.get("boxes", []) if isinstance(ocr_results, dict) else []
            }
        elif isinstance(ocr_results, list):
            # For text regions, process the list of dictionaries or nested lists
            
            # Try to detect if it's a string representation of a list
            if len(ocr_results) == 1 and isinstance(ocr_results[0], str) and ocr_results[0].startswith('['):
                # It's a string representation - try to parse it
                try:
                    import ast
                    parsed_results = ast.literal_eval(ocr_results[0])
                    
                    # Now process the parsed results
                    text_items = []
                    for item in parsed_results:
                        if isinstance(item, dict) and 'text' in item:
                            text_items.append(item['text'])
                    
                    content = {"text": "\n".join(text_items)}
                except:
                    # If parsing fails, use the raw string
                    content = {"text": str(ocr_results)}
            else:
                # Try to extract text from various formats
                text_items = []
                for item in ocr_results:
                    if isinstance(item, dict) and 'text' in item:
                        # Format: {'text': 'some text', 'confidence': 0.9, ...}
                        text_items.append(item['text'])
                    elif isinstance(item, list) and len(item) > 1:
                        # Format: [[bbox], [text, confidence]]
                        if isinstance(item[1], list) and len(item[1]) > 0:
                            text_items.append(item[1][0])
                        elif isinstance(item[1], str):
                            text_items.append(item[1])
                
                content = {"text": "\n".join(text_items)}
        else:
            # For any other format or empty results
            content = {"raw_data": str(ocr_results)}
            
        # Create the layout result
        layout_result = LayoutResult(
            region_id=f"region_{uuid.uuid4().hex}",
            region_type=region_type,
            bbox_raw=bbox,
            bbox_norm=norm_bbox,
            content=content,
            page=page
        )
        layout_results.append(layout_result)
    
    # Handle case where no regions were found
    if not layout_results:
        layout_results.append(LayoutResult(
            region_id=f"region_{uuid.uuid4().hex}",
            region_type="unknown",
            bbox_raw=[0, 0, width, height],
            bbox_norm=[0, 0, 1, 1],
            content={"text": "No regions detected"},
            page=page
        ))
    
    return LayoutPageResult(page=page, results=layout_results)
import os
import uuid
from typing import List
from pdf2image import convert_from_path

def convert_pdf_to_images(pdf_path: str) -> List[str]:
    """
    Convert all pages of a PDF into PNG images, save them to uploads/ as filename_page_#.png with a UUID suffix, and return a list of file paths.
    """
    # Ensure uploads directory exists
    os.makedirs("uploads", exist_ok=True)

    # Extract base filename (without extension)
    base_filename = os.path.splitext(os.path.basename(pdf_path))[0]
    unique_id = str(uuid.uuid4())

    # Convert PDF to images
    images = convert_from_path(pdf_path)
    image_paths = []
    for i, image in enumerate(images):
        image_filename = f"{base_filename}_page_{i+1}_{unique_id}.png"
        image_path = os.path.join("uploads", image_filename)
        image.save(image_path, "PNG")
        image_paths.append(image_path)
    return image_paths 
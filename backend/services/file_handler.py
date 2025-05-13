from fastapi import UploadFile # type: ignore
import os
import shutil
from typing import Union, BinaryIO
import uuid

# Ensure the uploads directory exists
os.makedirs("uploads", exist_ok=True)

def get_file_path(filename: str) -> str:
    """
    Get the full path to a file in the uploads directory
    
    Args:
        filename: The name of the file
        
    Returns:
        The full path to the file
    """
    return os.path.join("uploads", filename)

async def save_file(file: UploadFile) -> str:
    """
    Save an uploaded file to the uploads directory with a unique UUID filename.
    Returns the unique filename.
    """
    # Ensure uploads directory exists
    os.makedirs("uploads", exist_ok=True)

    # Extract file extension
    original_filename = file.filename or "unnamed_file"
    file_extension = original_filename.split(".")[-1]
    unique_filename = f"{uuid.uuid4()}.{file_extension}"
    file_path = os.path.join("uploads", unique_filename)

    # Save file
    with open(file_path, "wb") as buffer:
        content = await file.read()
        buffer.write(content)
    await file.seek(0)
    return unique_filename


# async def save_upload_file(upload_file: UploadFile, destination: str) -> str:
#     """
#     Saves an uploaded file to the specified destination.
    
#     Args:
#         upload_file: The uploaded file
#         destination: The filename for the destination (not full path)
        
#     Returns:
#         The full path where the file was saved
#     """
#     file_path = os.path.join("uploads", destination)
    
#     try:
#         # Use a memory-efficient approach to save the file
#         with open(file_path, "wb") as buffer:
#             shutil.copyfileobj(upload_file.file, buffer)
#     finally:
#         # Make sure to reset the file pointer
#         await upload_file.seek(0)
    
#     return file_path
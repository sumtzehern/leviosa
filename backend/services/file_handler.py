
from fastapi import UploadFile
import os
import shutil
from typing import Union, BinaryIO

# Ensure the uploads directory exists
os.makedirs("uploads", exist_ok=True)

async def save_upload_file(upload_file: UploadFile, destination: str) -> str:
    """
    Saves an uploaded file to the specified destination.
    
    Args:
        upload_file: The uploaded file
        destination: The filename for the destination (not full path)
        
    Returns:
        The full path where the file was saved
    """
    file_path = os.path.join("uploads", destination)
    
    try:
        # Use a memory-efficient approach to save the file
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(upload_file.file, buffer)
    finally:
        # Make sure to reset the file pointer
        await upload_file.seek(0)
    
    return file_path

def get_file_path(filename: str) -> str:
    """
    Get the full path to a file in the uploads directory
    
    Args:
        filename: The name of the file
        
    Returns:
        The full path to the file
    """
    return os.path.join("uploads", filename)

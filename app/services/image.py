import logging
import os
from uuid import uuid1
from fastapi import UploadFile
from fastapi.responses import JSONResponse

from app.models.charger import Charger


class ImageTypeError(Exception):
    def __init__(self, message):            
        # Call the base class constructor with the parameters it needs
        super().__init__(message)

class FileToLargeError(Exception):
    def __init__(self, message):            
        # Call the base class constructor with the parameters it needs
        super().__init__(message)

def save_image(myfile: UploadFile):
    
    allowed_extensions = ('.jpg', '.jpeg', '.png', '.gif')
    if not myfile.filename.lower().endswith(allowed_extensions):
        raise ImageTypeError("Only images allowed")
        #return JSONResponse(content={"error": "Only images allowed"}, status_code=403)
    
    if myfile.size > 1024 * 1024: # 1MB
        raise FileToLargeError("File size too large")
        #return JSONResponse(content={"error": "File size too large"}, status_code=403)
    
    extension = myfile.filename.split(".")[-1]
    unique_name = f"{uuid1()}.{extension}"
    image_path = os.path.join("app","image", unique_name)
    
    with open(image_path, "wb") as image_file:
        image_file.write(myfile.file.read())
    
    return (unique_name)


def get_image(image_name) -> bytes:
    image_path = os.path.join("app","image", image_name)
        
    if not os.path.exists(image_path):
        raise FileNotFoundError
    
    logging.info(f"Reading image {image_path}")
    
    with open(image_path, 'rb') as file:
        image_bytes: bytes = file.read()
    
    return image_bytes
import os
from uuid import uuid1
from fastapi import UploadFile
from fastapi.responses import JSONResponse


class ImageTypeError(Exception):
    def __init__(self, message):            
        # Call the base class constructor with the parameters it needs
        super().__init__(message)

class FileToLargeError(Exception):
    def __init__(self, message):            
        # Call the base class constructor with the parameters it needs
        super().__init__(message)

def save_image(file: UploadFile):
    
    allowed_extensions = ('.jpg', '.jpeg', '.png', '.gif')
    if not file.filename.lower().endswith(allowed_extensions):
        raise ImageTypeError("Only images allowed")
        #return JSONResponse(content={"error": "Only images allowed"}, status_code=403)
    
    if file.size > 1024 * 1024: # 1MB
        raise FileToLargeError("File size too large")
        #return JSONResponse(content={"error": "File size too large"}, status_code=403)
    
    extension = file.filename.split(".")[-1]
    unique_name = f"{uuid1()}.{extension}"
    image_path = os.path.join("app","image", unique_name)
    
    with open(image_path, "wb") as image_file:
        image_file.write(file.file.read())
    
    return (unique_name)
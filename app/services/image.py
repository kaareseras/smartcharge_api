import os
from uuid import uuid1
from fastapi import APIRouter, Depends, File, Form, UploadFile, status
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from app.models.charger import Charger
from app.routes.image import ImageResponse

def save_image(file: UploadFile, type: str, id: int, session: Session):
    if type not in ["charger"]:
        return JSONResponse(content={"error": "Invalid type"}, status_code=403)
    
    allowed_extensions = ('.jpg', '.jpeg', '.png', '.gif')
    if not file.filename.lower().endswith(allowed_extensions):
        return JSONResponse(content={"error": "Only images allowed"}, status_code=403)
    
    if file.size > 1024 * 1024: # 1MB
        return JSONResponse(content={"error": "File size too large"}, status_code=403)
    

    extension = file.filename.split(".")[-1]
    random_name = f"{uuid1()}.{extension}"
    image_path = os.path.join("app","image", random_name)

    if type == "charger":
        charger = session.query(Charger).filter(Charger.id == id).first()
        if not charger:
            return JSONResponse(content={"error": "Charger not found"}, status_code=404)
        else:
            charger.image_filename = random_name
            session.commit()
            session.refresh(charger)

    # if type == "car":
    #     car = session.query(Car).filter(Car.id == id).first()
    #     if not car:
    #         return JSONResponse(content={"error": "Car not found"}, status_code=400)    
    

    
    with open(image_path, "wb") as image_file:
        image_file.write(file.file.read())

        myImage = ImageResponse(file_name=random_name)

    
    return (myImage)


from fastapi import APIRouter, Depends, File, Form, UploadFile
from sqlalchemy.orm import Session

from app.config.database import get_session

from app.config.security import get_current_user
from app.responses.image import ImageResponse
from app.services.image import save_image


image_router = APIRouter(
    prefix="/image",
    tags=["Image"],
    responses={404: {"description": "Not found"}},
)

@image_router.post("")
async def create_upload_file(        
    type: str = Form(...),
    id: int = Form(...),
    file: UploadFile = File(...), 
    response_model=ImageResponse, 
    session: Session = Depends(get_session)
):
    
    return save_image(file, type, id, session)
    



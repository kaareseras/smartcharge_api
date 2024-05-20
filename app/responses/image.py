from pydantic import BaseModel


class ImageResponse(BaseModel):
    file_name: str
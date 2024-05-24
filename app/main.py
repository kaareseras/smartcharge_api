from fastapi import FastAPI
from app.routes import user, charger, car

def create_application():
    application = FastAPI()
    application.include_router(user.user_router)
    application.include_router(user.guest_router)
    application.include_router(user.auth_router)
    application.include_router(charger.charger_router)
    application.include_router(car.car_router)
    return application


app = create_application()


@app.get("/")
async def root():
    return {"message": "Hi, I am SmartCharge. Awesome - Your setrup is done & working."}
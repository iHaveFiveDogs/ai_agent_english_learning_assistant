from fastapi import APIRouter

router = APIRouter()

@router.get("/")
async def welcome():
    return {"message": "Welcome to the FastAPI application!"}

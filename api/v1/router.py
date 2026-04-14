from fastapi import APIRouter
from api.v1.endpoints import auth, transcription

router = APIRouter()

router.include_router(auth.router)

router.include_router(transcription.router)

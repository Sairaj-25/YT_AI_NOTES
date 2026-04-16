from fastapi import APIRouter
from api.v1.endpoints import auth, transcription, generate_note

router = APIRouter()

router.include_router(auth.router)

router.include_router(transcription.router)

router.include_router(generate_note.router)

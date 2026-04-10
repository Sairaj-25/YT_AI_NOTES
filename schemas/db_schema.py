from pydantic import BaseModel, EmailStr
from typing import List

# user schemas

class UserCreate(BaseModel):

    name: str
    email: EmailStr
    password: str

class UserLogin(BaseModel):

    username: EmailStr
    password: str

class NoteCreate(BaseModel):

    id: int
    youtube_link: str
    content: str
    owner_id: str

    class Config:
        from_attributes = True

class NoteResponse(BaseModel):
    """Schema for returning question data"""
    id: int
    youtube_link: str
    content: str
    owner_id: int

    class Config:
        from_attributes = True

class UserWithNotes(BaseModel):
    """Schema for user with their saved notes"""
    id: int
    email: EmailStr
    name: str
    notes:List[NoteResponse]

    class Config:
        from_attributes = True
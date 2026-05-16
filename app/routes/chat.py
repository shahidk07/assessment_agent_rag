from fastapi import APIRouter
from pydantic import BaseModel

from app.services.recommendation_service import (
    process_query
)


router = APIRouter()


class Message(BaseModel):
    role: str
    content: str


class ChatRequest(BaseModel):
    messages: list[Message]

@router.post("/chat")
def chat(request: ChatRequest):

    return process_query(request.messages)
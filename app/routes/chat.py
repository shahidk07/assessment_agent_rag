from fastapi import APIRouter
from pydantic import BaseModel

from app.services.recommendation_service import (
    process_query
)


router = APIRouter()


class ChatRequest(BaseModel):
    query: str


@router.post("/chat")
def chat(request: ChatRequest):

    return process_query(request.query)
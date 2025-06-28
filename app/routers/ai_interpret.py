from fastapi import APIRouter
from pydantic import BaseModel
from typing import List, Optional
from app.services.parser import parse_prompt

router = APIRouter()

# Pydantic models for response structure
class Shape(BaseModel):
    type: str
    x: int
    y: int
    width: Optional[int] = None
    height: Optional[int] = None
    radius: Optional[int] = None
    radiusX: Optional[int] = None
    radiusY: Optional[int] = None
    color: Optional[str] = None

class TextAnnotation(BaseModel):
    text: str
    x: int
    y: int
    fontSize: Optional[int] = 24
    color: Optional[str] = "black"

class InterpretResponse(BaseModel):
    shapes: List[Shape] = []
    texts: List[TextAnnotation] = []

class InterpretRequest(BaseModel):
    prompt: str

@router.post("/", response_model=InterpretResponse)
async def interpret_prompt(request: InterpretRequest):
    result = parse_prompt(request.prompt)
    return InterpretResponse(
        shapes=result["shapes"],
        texts=result["texts"]
    ) 
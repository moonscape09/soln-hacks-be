from fastapi import APIRouter
from pydantic import BaseModel, Field
from typing import List, Literal, Union, Annotated, Optional
from app.services.parser import parse_prompt

router = APIRouter()

# --- Shape Variants ---

class RectangleShape(BaseModel):
    type: Literal["rectangle"]
    x: int
    y: int
    width: int
    height: int
    color: Optional[str]

class CircleShape(BaseModel):
    type: Literal["circle"]
    x: int
    y: int
    radius: int
    color: Optional[str]

class EllipseShape(BaseModel):
    type: Literal["ellipse"]
    x: int
    y: int
    radiusX: int
    radiusY: int
    color: Optional[str]

class LineShape(BaseModel):
    type: Literal["line"]
    points: List[float]  # Each point is [x, y]
    stroke: str
    strokeWidth: int


class TextShape(BaseModel):
    type: Literal["text"]
    text: str
    x: int
    y: int
    fontSize: Optional[int] = 24
    color: Optional[str] = "black"

# --- Discriminated Union using Annotated + Field ---
Shape = Annotated[
    Union[RectangleShape, CircleShape, EllipseShape, LineShape, TextShape],
    Field(discriminator="type")
]

# --- API Models ---

class InterpretRequest(BaseModel):
    prompt: str

class InterpretResponse(BaseModel):
    shapes: List[Shape]

# --- Endpoint ---

@router.post("/", response_model=InterpretResponse)
async def interpret_prompt(request: InterpretRequest):
    result = parse_prompt(request.prompt)
    return InterpretResponse(shapes=result["shapes"])

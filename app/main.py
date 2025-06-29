from fastapi import FastAPI
from .routers import ai_interpret
from app.routers import session

app = FastAPI()

app.include_router(ai_interpret.router, prefix="/api/interpret", tags=["AI Interpret"])
app.include_router(session.router, prefix="/api", tags=["Session"])


@app.get("/")
async def root():
    return {"message": "Hello World"}

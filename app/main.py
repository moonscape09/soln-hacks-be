from fastapi import FastAPI
from .routers import ai_interpret

app = FastAPI()

app.include_router(ai_interpret.router, prefix="/api/interpret", tags=["AI Interpret"])


@app.get("/")
async def root():
    return {"message": "Hello World"}

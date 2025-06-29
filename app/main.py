from fastapi import FastAPI
from .routers import ai_interpret
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

#Allowed addresses
origins = [
    "http://localhost:3000",  # Frontend URL
    "http://127.0.0.1:3000",
    "*",  # Allow all origins (not recommended for production)
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(ai_interpret.router, prefix="/api/interpret", tags=["AI Interpret"])


@app.get("/")
async def root():
    return {"message": "Hello World"}

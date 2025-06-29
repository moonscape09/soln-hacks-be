from fastapi import APIRouter, HTTPException
from app.db.mongo import get_collection
from datetime import datetime

router = APIRouter()

@router.post("/save")
def save_board(data: dict):
    coll = get_collection("sessions")
    doc = data.copy()
    doc["created_at"] = datetime.utcnow().isoformat()
    if "_id" not in doc:
        raise HTTPException(status_code=400, detail="_id (session id) is required")
    coll.replace_one({"_id": doc["_id"]}, doc, upsert=True)
    return {"status": "ok"}

@router.get("/session/{session_id}")
def get_board(session_id: str):
    coll = get_collection("sessions")
    doc = coll.find_one({"_id": session_id})
    if not doc:
        raise HTTPException(status_code=404, detail="Session not found")
    doc["_id"] = str(doc["_id"])  # Ensure JSON serializable
    return doc 
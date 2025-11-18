import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List

from database import db, create_document, get_documents
from schemas import Investor, Contribution

TARGET_AMOUNT = 125000.0

app = FastAPI(title="Fintech VIP Fundraiser API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def root():
    return {"status": "ok", "service": "backend", "message": "VIP Fundraiser API running"}

@app.get("/test")
def test_database():
    response = {
        "backend": "✅ Running",
        "database": "❌ Not Available",
        "database_url": "❌ Not Set",
        "database_name": "❌ Not Set",
        "connection_status": "Not Connected",
        "collections": []
    }
    try:
        if db is not None:
            response["database"] = "✅ Available"
            response["database_url"] = "✅ Set" if os.getenv("DATABASE_URL") else "❌ Not Set"
            response["database_name"] = os.getenv("DATABASE_NAME") or "❌ Not Set"
            try:
                cols = db.list_collection_names()
                response["collections"] = cols[:10]
                response["database"] = "✅ Connected & Working"
                response["connection_status"] = "Connected"
            except Exception as e:
                response["database"] = f"⚠️ Connected but Error: {str(e)[:80]}"
        else:
            response["database"] = "⚠️ Available but not initialized"
    except Exception as e:
        response["database"] = f"❌ Error: {str(e)[:120]}"
    return response

# --- Fundraiser Endpoints ---

@app.post("/api/investors", response_model=dict)
def create_investor(investor: Investor):
    try:
        investor_id = create_document("investor", investor)
        return {"inserted_id": investor_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/investors", response_model=List[dict])
def list_investors(limit: int = 50):
    try:
        docs = get_documents("investor", {}, limit)
        # basic obfuscation: mask email
        for d in docs:
            if "email" in d:
                parts = d["email"].split("@")
                if len(parts) == 2:
                    d["email"] = parts[0][:2] + "***@" + parts[1]
        return docs
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/contributions", response_model=dict)
def create_contribution(contribution: Contribution):
    try:
        contrib_id = create_document("contribution", contribution)
        return {"inserted_id": contrib_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/contributions", response_model=List[dict])
def list_contributions(limit: int = 100):
    try:
        docs = get_documents("contribution", {}, limit)
        return docs
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/progress", response_model=dict)
def get_progress():
    try:
        contribs = get_documents("contribution", {}, None)
        total = sum(float(c.get("amount", 0)) for c in contribs)
        percent = min(100.0, (total / TARGET_AMOUNT) * 100.0 if TARGET_AMOUNT > 0 else 0.0)
        return {
            "target": TARGET_AMOUNT,
            "total": round(total, 2),
            "percent": round(percent, 2),
            "remaining": round(max(0.0, TARGET_AMOUNT - total), 2),
            "count": len(contribs)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)

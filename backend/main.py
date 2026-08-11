from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from backend.agents.privacy.gatekeeper import gatekeeper

app = FastAPI(
    title="DRY AI Platform API",
    description="Secure, Air-gapped Modular AI Backend",
    version="1.0.0"
)

# CORS setup (Allow all for development, restrict in production)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"message": "DRY AI Platform Core Engine is online."}

@app.get("/health")
async def health_check():
    return {"status": "System healthy and secure."}

class PrivacyRequest(BaseModel):
    text: str

@app.post("/api/v1/anonymize")
async def anonymize_text(request: PrivacyRequest):
    """
    Core Privacy Gatekeeper Endpoint.
    Detects and redacts PII before processing.
    """
    clean_text = gatekeeper.anonymize_text(request.text)
    return {
        "anonymized_text": clean_text
    }

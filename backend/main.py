from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
from backend.agents.privacy.gatekeeper import gatekeeper
from backend.agents.rag.engine import rag_engine
from backend.agents.portals.healthcare import healthcare_agent

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

class DocumentRequest(BaseModel):
    text: str
    meta: Optional[dict] = None

class SearchQuery(BaseModel):
    query: str
    top_k: int = 3

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

@app.post("/api/v1/knowledge/index")
async def index_document(request: DocumentRequest):
    """
    Secure Indexing Endpoint.
    Passes document through Gatekeeper, then indexes it in Qdrant.
    """
    # 1. Anonymize the data (The DRY Platform Guarantee)
    clean_text = gatekeeper.anonymize_text(request.text)
    
    # 2. Index the clean data
    success = rag_engine.index_document(clean_text, request.meta)
    
    return {
        "status": "success" if success else "failed",
        "indexed_text": clean_text
    }

@app.post("/api/v1/knowledge/search")
async def search_knowledge(request: SearchQuery):
    """
    Secure Search Endpoint.
    Anonymizes the query, then searches Qdrant for context.
    """
    # 1. Anonymize the query so we don't leak PII into search logs/vectors
    clean_query = gatekeeper.anonymize_text(request.query)
    
    # 2. Retrieve context
    context_chunks = rag_engine.retrieve_context(clean_query, top_k=request.top_k)
    
    return {
        "anonymized_query": clean_query,
        "context": context_chunks
    }

class ChatRequest(BaseModel):
    question: str

@app.post("/api/v1/portals/healthcare/chat")
async def healthcare_chat(request: ChatRequest):
    """
    Phase 4: The Healthcare Agent Portal.
    Full Loop: Anonymize -> Search -> Generate
    """
    # 1. Intercept and Anonymize
    clean_question = gatekeeper.anonymize_text(request.question)
    
    # 2. Retrieve relevant medical context from our Qdrant vector store
    context = rag_engine.retrieve_context(clean_question, top_k=3)
    
    # 3. Stream to the local LLM to get the final answer
    answer = healthcare_agent.generate_response(clean_question, context)
    
    return {
        "anonymized_question": clean_question,
        "answer": answer
    }

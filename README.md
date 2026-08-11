# DRY AI Platform (Don't Repeat Yourself)

An air-gapped, zero-to-production Enterprise AI platform designed for highly secure environments like Healthcare and Finance.

## 🚀 Architecture Overview

The DRY Platform operates on a strictly air-gapped architecture using Docker. It guarantees that sensitive PII (Personally Identifiable Information) never touches the Large Language Model or the Vector Database.

The flow is: **Privacy Gatekeeper -> RAG Engine -> Local LLM Orchestrator**

### 1. Privacy Gatekeeper
Powered by **Microsoft Presidio** and **SpaCy**, the Gatekeeper acts as a firewall for data. It actively intercepts incoming text and scrubs sensitive entities (Names, Phone Numbers, Email Addresses, Dates, and Locations) before replacing them with anonymized tags (e.g., `<PERSON>`).

### 2. RAG Engine
Powered by **Haystack 2.x** and **Qdrant**. The RAG Engine takes the completely anonymized text, chunks it, embeds it using `sentence-transformers/all-MiniLM-L6-v2`, and stores it in a local vector database. When a user asks a question, it retrieves the most relevant semantic chunks.

### 3. Healthcare Portal Agent (Local LLM)
Powered by **Llama 3.1 (8B)** running on **Ollama**. The Agent receives the user's question and the retrieved, anonymized context. It is strictly prompted to refuse giving medical advice and to only extract answers based on the secure context provided.

## 🛠️ Tech Stack
* **Backend**: FastAPI (Python 3.13)
* **Vector DB**: Qdrant (Docker)
* **LLM Runner**: Ollama (Docker)
* **Model**: Llama 3.1 8B (4-bit quantized)
* **RAG Framework**: Haystack 2.x
* **Privacy Engine**: Microsoft Presidio
* **Database**: PostgreSQL (Docker - For future auth/history)

## 📦 How to Run

1. **Start the Infrastructure**:
```bash
docker-compose up -d
```

2. **Pull the LLM (First time only)**:
```bash
docker exec dry_ollama ollama pull llama3.1
```

3. **Start the API Server**:
```bash
source "/path/to/global_venv/bin/activate"
uvicorn backend.main:app --reload --port 8000
```

4. **Access the API**:
Navigate to `http://localhost:8000/docs` to test the endpoints via Swagger UI.

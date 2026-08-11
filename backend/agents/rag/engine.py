import os
from haystack import Document, Pipeline
from haystack.components.embedders import SentenceTransformersTextEmbedder, SentenceTransformersDocumentEmbedder
from haystack.components.preprocessors import DocumentSplitter
from haystack.components.writers import DocumentWriter
from haystack_integrations.document_stores.qdrant import QdrantDocumentStore
from haystack_integrations.components.retrievers.qdrant import QdrantEmbeddingRetriever

class RAGEngine:
    def __init__(self):
        # Connect to Qdrant running in Docker
        self.document_store = QdrantDocumentStore(
            url="http://localhost:6333",
            index="dry_knowledge_base",
            embedding_dim=384, # Dimension for all-MiniLM-L6-v2
            recreate_index=False
        )
        
        # Setup Embedders using local sentence-transformers
        # We use a lightweight model suitable for quick RAG lookups
        self.doc_embedder = SentenceTransformersDocumentEmbedder(model="sentence-transformers/all-MiniLM-L6-v2")
        self.doc_embedder.warm_up()
        
        self.text_embedder = SentenceTransformersTextEmbedder(model="sentence-transformers/all-MiniLM-L6-v2")
        self.text_embedder.warm_up()
        
        # Build Indexing Pipeline
        self.indexing_pipeline = Pipeline()
        self.indexing_pipeline.add_component("splitter", DocumentSplitter(split_by="sentence", split_length=5))
        self.indexing_pipeline.add_component("embedder", self.doc_embedder)
        self.indexing_pipeline.add_component("writer", DocumentWriter(self.document_store))
        
        self.indexing_pipeline.connect("splitter", "embedder")
        self.indexing_pipeline.connect("embedder", "writer")

        # Build Retrieval Pipeline
        self.retrieval_pipeline = Pipeline()
        self.retrieval_pipeline.add_component("embedder", self.text_embedder)
        self.retrieval_pipeline.add_component("retriever", QdrantEmbeddingRetriever(document_store=self.document_store))
        self.retrieval_pipeline.connect("embedder.embedding", "retriever.query_embedding")

    def index_document(self, text: str, meta: dict = None):
        """Indexes an anonymized document into Qdrant."""
        doc = Document(content=text, meta=meta or {})
        self.indexing_pipeline.run({
            "splitter": {"documents": [doc]}
        })
        return True
        
    def retrieve_context(self, query: str, top_k: int = 3):
        """Retrieves relevant chunks for a given query."""
        results = self.retrieval_pipeline.run({
            "embedder": {"text": query},
            "retriever": {"top_k": top_k}
        })
        documents = results.get("retriever", {}).get("documents", [])
        return [doc.content for doc in documents]

# Singleton instance
rag_engine = RAGEngine()

from haystack import Pipeline
from haystack.components.builders import PromptBuilder
from haystack_integrations.components.generators.ollama import OllamaGenerator

class HealthcarePortalAgent:
    def __init__(self):
        # Strict system prompt ensuring HIPAA/GDPR-like compliance behavior
        prompt_template = """
        You are an expert Healthcare AI Assistant operating within a secure, air-gapped environment.
        You must ONLY answer the user's question using the provided context.
        If the context does not contain the answer, say "I cannot answer this based on the secure context provided."
        Do NOT guess or use outside knowledge.
        
        Context:
        {% for doc in context %}
            {{ doc }}
        {% endfor %}
        
        Question: {{ question }}
        Answer:
        """
        
        self.prompt_builder = PromptBuilder(template=prompt_template)
        
        # Connect to our local Docker Ollama instance
        self.llm = OllamaGenerator(
            model="llama3.1",
            url="http://localhost:11434"
        )
        
        # Build the RAG Generation Pipeline
        self.pipeline = Pipeline()
        self.pipeline.add_component("prompt_builder", self.prompt_builder)
        self.pipeline.add_component("llm", self.llm)
        self.pipeline.connect("prompt_builder", "llm")
        
    def generate_response(self, question: str, context: list[str]) -> str:
        """Generates a secure answer based on the retrieved anonymized context."""
        result = self.pipeline.run({
            "prompt_builder": {
                "question": question,
                "context": context
            }
        })
        return result["llm"]["replies"][0]

# Singleton instance
healthcare_agent = HealthcarePortalAgent()

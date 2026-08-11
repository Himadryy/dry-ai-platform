from presidio_analyzer import AnalyzerEngine
from presidio_anonymizer import AnonymizerEngine

class PrivacyGatekeeper:
    def __init__(self):
        # Initialize the Presidio engines
        # Note: In a production environment, you might want to load models asynchronously or during startup
        self.analyzer = AnalyzerEngine()
        self.anonymizer = AnonymizerEngine()

    def anonymize_text(self, text: str) -> str:
        """
        Detects PII (Personally Identifiable Information) in the given text 
        and replaces it with anonymous placeholders (e.g., <PERSON>, <EMAIL_ADDRESS>).
        """
        if not text:
            return text
            
        # Analyze the text for PII entities
        results = self.analyzer.analyze(
            text=text,
            entities=[], # Empty list defaults to all supported entities
            language='en'
        )
        
        # Anonymize the text based on analyzer results
        anonymized_result = self.anonymizer.anonymize(
            text=text,
            analyzer_results=results
        )
        
        return anonymized_result.text

# Singleton instance to be imported and used across the platform
gatekeeper = PrivacyGatekeeper()

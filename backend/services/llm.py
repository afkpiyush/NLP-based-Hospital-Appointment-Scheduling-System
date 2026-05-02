"""
LLM Service Module - Wrapper for Groq API using LangChain
"""
import os
from typing import Optional
from langchain_groq import ChatGroq
from dotenv import load_dotenv

load_dotenv()

class LLMModel:
    """Wrapper for ChatGroq LLM"""
    
    def __init__(self, model_name: str = None):
        self.api_key = os.getenv("GROQ_API_KEY")
        self.model_name = model_name or os.getenv("GROQ_MODEL", "llama3-70b-8192")
        
        if not self.api_key:
            print("Warning: GROQ_API_KEY not found in environment variables.")
    
    def get_model(self):
        """Return a ChatGroq instance"""
        if self.api_key:
            return ChatGroq(
                model=self.model_name,
                groq_api_key=self.api_key,
                temperature=0.7,
                max_tokens=None,
                timeout=None,
                max_retries=2,
            )
        else:
            # Fallback for development without API key
            from langchain_core.language_models.fake import FakeListLLM
            return FakeListLLM(responses=["This is a mock response because no API key was provided."])

# Singleton instance
_llm_instance: Optional[LLMModel] = None

def get_llm_model() -> LLMModel:
    """Get or create LLM instance"""
    global _llm_instance
    if _llm_instance is None:
        _llm_instance = LLMModel()
    return _llm_instance

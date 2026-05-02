import os

try:
    from langchain_groq import ChatGroq
except ImportError:
    ChatGroq = None

from dotenv import load_dotenv
load_dotenv()

api_key = os.getenv("GROQ_API_KEY")


class _MockStructuredOutput:
    def invoke(self, messages):
        return {"next": "FINISH", "reasoning": "Mock fallback used for local execution."}


class _MockChatModel:
    def invoke(self, prompt):
        return "Mock response for local execution."

    def with_structured_output(self, schema):
        return _MockStructuredOutput()


class LLMModel:
    def __init__(self, model_name="llama3-70b-8192"):
        self.model_name = model_name

    def get_model(self):
        if api_key and ChatGroq is not None:
            return ChatGroq(model=self.model_name, api_key=api_key)
        return _MockChatModel()

if __name__ == "__main__":
    llm_instance = LLMModel(model_name="llama3-70b-8192")  
    llm_model = llm_instance.get_model()
    response=llm_model.invoke("hi")

    print(response)
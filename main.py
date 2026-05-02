from services.llm import LLMModel
from agents.builder import build_graph
from langchain_core.messages import HumanMessage

llm_model = LLMModel().get_model()

app = build_graph(llm_model)

initial_state = {
    "messages": [HumanMessage(content="I want to book appointment with cardiologist")],
    "id_number": 101,
    "next": "",
    "query": "",
    "current_reasoning": "",
}

result = app.invoke(initial_state)

print(result)
from agents.builder import build_graph
from services.llm import LLMModel


class DoctorAppointmentAgent:
    def __init__(self):
        self.llm_model = LLMModel().get_model()

    def workflow(self):
        return build_graph(self.llm_model)

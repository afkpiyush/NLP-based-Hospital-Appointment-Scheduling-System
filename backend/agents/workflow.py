"""
Workflow Execution Service
Handles the invocation of the LangGraph healthcare assistant
"""
from typing import Dict, Any, List
from langchain_core.messages import HumanMessage, AIMessage
from .builder import build_healthcare_graph
from ..services.llm import get_llm_model

class HealthcareWorkflow:
    """Manages the execution of the multi-agent healthcare graph"""
    
    def __init__(self):
        self.llm_model = get_llm_model().get_model()
        self.graph = build_healthcare_graph(self.llm_model)
    
    async def execute(self, user_input: str, user_id: str, id_number: int = 0, history: List = None) -> Dict[str, Any]:
        """
        Execute the workflow for a given user input
        """
        # Prepare state
        messages = history or []
        messages.append(HumanMessage(content=user_input))
        
        initial_state = {
            "messages": messages,
            "user_id": user_id,
            "id_number": id_number,
            "query": user_input,
            "next": "",
            "current_reasoning": "",
            "step_count": 0,
            "max_steps": 15
        }
        
        # Run graph
        result = self.graph.invoke(initial_state, config={"recursion_limit": 25})
        
        # Format response
        return {
            "messages": [
                {"role": "user" if isinstance(m, HumanMessage) else "assistant", "content": m.content}
                for m in result["messages"]
            ],
            "current_reasoning": result.get("current_reasoning", ""),
            "next_node": result.get("next", "FINISH")
        }

# Singleton instance
_workflow_instance = None

def get_workflow():
    """Get or create workflow instance"""
    global _workflow_instance
    if _workflow_instance is None:
        _workflow_instance = HealthcareWorkflow()
    return _workflow_instance

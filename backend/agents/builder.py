"""
LangGraph Builder for Complete AI Healthcare Assistant
Integrates all specialized agents into a unified workflow
"""
from langgraph.graph import StateGraph, START, END
from .state import AgentState
from .supervisor import supervisor_node

# Import backend agents
from .symptom_analysis_node import symptom_analysis_node
from .medical_reasoning_node import medical_reasoning_node
from .specialist_recommendation_node import specialist_recommendation_node
from .location_availability_node import location_availability_node
from .booking_node import booking_node
from .chat_node import chat_conversation_node
from .information_node import information_node


def build_healthcare_graph(llm_model):
    """
    Build the complete multi-agent graph with 8 specialized agents
    """
    
    graph = StateGraph(AgentState)
    
    # Add supervisor (Router)
    graph.add_node("supervisor", supervisor_node(llm_model))
    
    # Add specialized agents
    graph.add_node("symptom_analysis", symptom_analysis_node(llm_model))
    graph.add_node("medical_reasoning", medical_reasoning_node(llm_model))
    graph.add_node("specialist_recommendation", specialist_recommendation_node(llm_model))
    graph.add_node("location_availability", location_availability_node(llm_model))
    graph.add_node("booking_node", booking_node(llm_model))
    graph.add_node("chat_node", chat_conversation_node(llm_model))
    graph.add_node("information_node", information_node(llm_model))
    
    # Set entry point
    graph.add_edge(START, "supervisor")
    
    # Note: Each node uses Command(goto="supervisor") to return control to the supervisor
    # The supervisor uses Command(goto=END) or Command(goto="node_name") for routing
    
    # Compile and return the graph
    return graph.compile()

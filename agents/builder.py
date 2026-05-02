"""
LangGraph Builder for Multi-Agent Healthcare System
Constructs the complete agentic workflow with all specialized agents
"""
from langgraph.graph import StateGraph, START
from agents.state import AgentState
from agents.supervisor import supervisor_node

from agents.information_node import information_node
from agents.booking_node import booking_node


def build_graph(llm_model):
    """
    Build the complete multi-agent graph
    
    Agent Structure:
    - supervisor: Main router (evaluates user intent and routes to appropriate agent)
    - booking_node: Books/reschedules/cancels appointments
    - information_node: Provides general information
    """
    
    graph = StateGraph(AgentState)
    
    # Add supervisor node (main router)
    graph.add_node("supervisor", supervisor_node(llm_model))

    # Add lightweight local agents
    graph.add_node("information_node", information_node(llm_model))
    graph.add_node("booking_node", booking_node(llm_model))
    
    # Set entry point
    graph.add_edge(START, "supervisor")
    
    # Compile and return the graph
    return graph.compile()
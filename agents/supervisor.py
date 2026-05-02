from langgraph.types import Command
from langgraph.graph import END
from langchain_core.messages import HumanMessage
from prompts.prompt import get_extended_system_prompt
from agents.state import Router, AgentState


def supervisor_node(llm_model):
    """
    Enhanced Supervisor Agent
    Routes user queries to appropriate specialized agents
    Supports new healthcare system features
    """

    def node(state: AgentState):
        
        # Prepare context for routing decision
        messages = [
            {"role": "system", "content": get_extended_system_prompt()},
            {"role": "user", "content": f"user's identification number is {state.get('id_number', 0)}"},
            {"role": "user", "content": f"preferred language is {state.get('language_preference', 'EN')}"},
        ]
        
        # Add conversation history
        if state.get("messages"):
            for msg in state["messages"]:
                if hasattr(msg, 'content'):
                    messages.append({"role": "user", "content": msg.content})
        
        # Add current query if present
        if state.get("query"):
            messages.append({"role": "user", "content": state["query"]})

        # Get routing decision from LLM
        response = llm_model.with_structured_output(Router).invoke(messages)
        
        goto = response["next"]
        
        if goto == "FINISH":
            goto = END
        
        # Increment step counter for recursion prevention
        step_count = state.get("step_count", 0) + 1
        max_steps = state.get("max_steps", 15)
        
        # Force finish if too many steps
        if step_count >= max_steps:
            goto = END
        
        return Command(
            goto=goto,
            update={
                "next": goto,
                "current_reasoning": response.get("reasoning", ""),
                "step_count": step_count
            },
        )

    return node
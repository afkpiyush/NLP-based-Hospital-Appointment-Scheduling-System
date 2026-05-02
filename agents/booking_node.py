from langgraph.types import Command
from langchain_core.messages import AIMessage

def booking_node(llm_model):

    def node(state):
        result_message = "Mock booking agent response: appointment workflow handled locally."

        return Command(
            update={
                "messages": state["messages"] + [
                    AIMessage(content=result_message)
                ]
            },
            goto="supervisor",
        )

    return node
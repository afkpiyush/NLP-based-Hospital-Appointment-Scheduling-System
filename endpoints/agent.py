from fastapi import FastAPI
from agent import DoctorAppointmentAgent
from langchain_core.messages import HumanMessage
from models.user import UserQuery
    
agent = DoctorAppointmentAgent()
app = FastAPI()

@app.post("/execute")
def execute_agent(user_input: UserQuery):
    app_graph = agent.workflow()
    
    # Prepare agent state as expected by the workflow
    input = [
        HumanMessage(content=user_input.messages)
    ]
    query_data = {
        "messages": input,
        "id_number": user_input.id_number,
        "next": "",
        "query": "",
        "current_reasoning": "",
    }
    #config = {"configurable": {"thread_id": "1", "recursion_limit": 100}}  

    response = app_graph.invoke(query_data,config={"recursion_limit": 20})
    return {"messages": response["messages"]}

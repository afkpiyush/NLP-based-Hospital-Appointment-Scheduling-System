"""
Information Agent Node
Provides general hospital information, doctor details, and FAQs
"""
from langgraph.types import Command
from langchain_core.messages import AIMessage
from langchain_core.prompts.chat import ChatPromptTemplate
from langchain.agents import create_agent, tool
from pydantic import BaseModel, Field
from typing import List


@tool
def get_hospital_info() -> str:
    """
    Get general information about the hospital
    """
    return """
    Healthcare Plus Hospital
    Location: 123 Wellness Way, Metro City
    Emergency Contact: 911 or (555) 0123-4567
    Operating Hours: 24/7 for Emergency, 8 AM - 8 PM for Consultations
    Specializations: Cardiology, Neurology, Pediatrics, Orthopedics, Gastroenterology, Oncology.
    """


@tool
def get_doctor_faqs() -> str:
    """
    Get frequently asked questions about doctors and appointments
    """
    return """
    FAQs:
    1. How do I book an appointment? - You can book via this chat or call our reception.
    2. What documents do I need? - Please bring your ID card and previous medical records.
    3. Are online consultations available? - Yes, for follow-ups after the initial physical examination.
    4. What are the consultation fees? - Fees vary by specialist, typically between $50 and $200.
    """


def information_node(llm_model):
    """
    Information Agent
    - Provides hospital and doctor information
    - Answers FAQs
    - Educates users on platform features
    """
    
    def node(state):
        system_prompt = """
        You are a hospital information specialist.
        
        Your role is to:
        1. Answer user questions about hospital facilities and services
        2. Provide details about doctor specializations and qualifications
        3. Answer FAQs about appointments and policies
        4. Guide users on how to use the healthcare platform
        
        Tools Available:
        - get_hospital_info: Basic hospital details
        - get_doctor_faqs: Common questions and answers
        """
        
        prompt = ChatPromptTemplate.from_messages([
            ("system", system_prompt),
            ("placeholder", "{messages}"),
        ])
        
        agent = create_agent(
            model=llm_model,
            tools=[get_hospital_info, get_doctor_faqs],
            prompt=prompt,
        )
        
        result = agent.invoke(state)
        
        final_message = result.get("messages", [])
        if final_message:
            last_message = final_message[-1]
            response_text = last_message.content if hasattr(last_message, 'content') else str(last_message)
        else:
            response_text = "Information request processed."
            
        return Command(
            update={
                "messages": state["messages"] + [AIMessage(content=response_text)],
                "current_reasoning": "Information request handled"
            },
            goto="supervisor"
        )
    
    return node

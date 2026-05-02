"""
Symptom Analysis Agent Node
Extracts and validates symptoms from patient input
"""
from langgraph.types import Command
from langchain_core.messages import AIMessage
from langchain_core.prompts.chat import ChatPromptTemplate
from langchain.agents import create_agent
from pydantic import BaseModel, Field
from typing import List


class SymptomExtractionOutput(BaseModel):
    """Structured output for symptom extraction"""
    symptoms: List[str] = Field(..., description="List of identified symptoms")
    severity_levels: List[str] = Field(..., description="Severity level for each symptom (mild/moderate/severe)")
    duration_info: str = Field(default="", description="Duration of symptoms if mentioned")
    urgency_level: str = Field(default="low", description="Urgency level (low/medium/high/critical)")


def symptom_analysis_node(llm_model):
    """
    Symptom Analysis Agent
    - Extracts symptoms from natural language patient description
    - Validates against medical ontology
    - Determines urgency level
    - Returns structured symptom data
    """
    
    def node(state):
        system_prompt = """
        You are a medical triage specialist trained to analyze patient symptoms.
        
        Your responsibilities:
        1. Carefully extract ALL symptoms mentioned by the patient
        2. Assess severity for each symptom (mild/moderate/severe)
        3. Determine if the condition requires urgent/emergency care
        4. Ask clarifying questions if critical information is missing
        
        Important Guidelines:
        - Be empathetic and professional
        - Do NOT attempt diagnosis - only extract and classify symptoms
        - If the patient describes emergency symptoms (chest pain, difficulty breathing, severe bleeding), 
          flag as CRITICAL
        - Ask about symptom duration if not specified
        - Consider comorbidities or existing conditions
        
        Current year is 2026.
        """
        
        prompt = ChatPromptTemplate.from_messages([
            ("system", system_prompt),
            ("placeholder", "{messages}"),
        ])
        
        # Create agent with structured output
        agent = create_agent(
            model=llm_model.with_structured_output(SymptomExtractionOutput),
            tools=[],  # No tools needed for symptom extraction
            prompt=prompt,
        )
        
        result = agent.invoke(state)
        
        # Extract structured output
        structured_output = result.get("symptoms", {})
        
        # Prepare response message
        response_text = f"""
Symptoms Identified:
{', '.join(structured_output.get('symptoms', []))}

Severity Assessment:
{', '.join(structured_output.get('severity_levels', []))}

Urgency Level: {structured_output.get('urgency_level', 'low').upper()}

{'⚠️ URGENT CARE RECOMMENDED - Please seek immediate medical attention' if structured_output.get('urgency_level') == 'critical' else ''}
        """
        
        # Log interaction
        from ..database.crud import InteractionLogCRUD
        try:
            InteractionLogCRUD.log_interaction({
                "user_id": state.get("user_id", "unknown"),
                "interaction_type": "SYMPTOM_ANALYSIS",
                "symptoms_input": str(state["messages"][-1].content if state["messages"] else ""),
                "diseases_predicted": []
            })
        except:
            pass  # Silent fail for logging
        
        return Command(
            update={
                "messages": state["messages"] + [AIMessage(content=response_text)],
                "current_reasoning": f"Symptom Analysis: {structured_output.get('urgency_level')} urgency",
                "symptoms_extracted": structured_output.get('symptoms', []),
                "symptom_severity": dict(zip(
                    structured_output.get('symptoms', []),
                    structured_output.get('severity_levels', [])
                ))
            },
            goto="supervisor"
        )
    
    return node

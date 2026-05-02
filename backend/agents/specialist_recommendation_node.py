"""
Specialist Recommendation Agent Node
Maps diseases to appropriate medical specialists
"""
from langgraph.types import Command
from langchain_core.messages import AIMessage
from langchain_core.prompts.chat import ChatPromptTemplate
from langchain.agents import create_agent
from pydantic import BaseModel, Field
from typing import List
import json


class SpecialistRecommendationOutput(BaseModel):
    """Specialist recommendation output"""
    specialists: List[str] = Field(..., description="List of recommended specialists ranked by priority")
    justifications: dict = Field(..., description="Justification for each specialist recommendation")
    primary_specialist: str = Field(..., description="Most recommended specialist")


# Disease to Specialist Mapping
DISEASE_SPECIALIST_MAP = {
    "Common Cold": ["General Physician", "Family Medicine"],
    "Influenza (Flu)": ["General Physician", "Infectious Disease Specialist"],
    "COVID-19": ["General Physician", "Infectious Disease Specialist", "Pulmonologist"],
    "Bacterial Pneumonia": ["Pulmonologist", "Infectious Disease Specialist", "Intensivist"],
    "Migraine": ["Neurologist", "General Physician"],
    "Allergies": ["Allergist/Immunologist", "Dermatologist", "General Physician"],
    "Hypertension": ["Cardiologist", "General Physician", "Internal Medicine"],
    "Diabetes": ["Endocrinologist", "Diabetologist", "General Physician"],
    "Anxiety Disorder": ["Psychiatrist", "Clinical Psychologist", "General Physician"],
    "Gastritis": ["Gastroenterologist", "General Physician", "Internal Medicine"],
    "Asthma": ["Pulmonologist", "Allergist", "General Physician"],
    "Bronchitis": ["Pulmonologist", "General Physician"],
    "Thyroid Disorder": ["Endocrinologist", "General Physician"],
    "Skin Infection": ["Dermatologist", "General Physician"],
    "Joint Pain/Arthritis": ["Rheumatologist", "Orthopedic Surgeon", "General Physician"],
    "Back Pain": ["Orthopedic Surgeon", "Neurologist", "Physiotherapist"],
    "Urinary Tract Infection": ["Urologist", "General Physician"],
    "Eye Problems": ["Ophthalmologist", "General Physician"],
    "Ear/Nose/Throat": ["ENT Specialist", "General Physician"],
    "Depression": ["Psychiatrist", "Clinical Psychologist", "General Physician"]
}

# Specialist Information
SPECIALIST_INFO = {
    "General Physician": {
        "description": "Primary care physician for general health",
        "qualifications": ["MBBS", "MD in General Medicine or Family Medicine"],
        "experience_importance": "High"
    },
    "Pulmonologist": {
        "description": "Specialist in respiratory/lung diseases",
        "qualifications": ["MBBS", "MD/DM in Pulmonology"],
        "experience_importance": "High for serious conditions"
    },
    "Cardiologist": {
        "description": "Specialist in heart and cardiovascular diseases",
        "qualifications": ["MBBS", "MD in General Medicine", "DM in Cardiology"],
        "experience_importance": "Very High"
    },
    "Neurologist": {
        "description": "Specialist in nervous system disorders",
        "qualifications": ["MBBS", "MD in General Medicine", "DM in Neurology"],
        "experience_importance": "High"
    },
    "Gastroenterologist": {
        "description": "Specialist in digestive system disorders",
        "qualifications": ["MBBS", "MD in General Medicine", "DM in Gastroenterology"],
        "experience_importance": "High"
    },
    "Endocrinologist": {
        "description": "Specialist in hormonal and metabolic disorders",
        "qualifications": ["MBBS", "MD in General Medicine", "DM in Endocrinology"],
        "experience_importance": "High"
    },
    "Dermatologist": {
        "description": "Specialist in skin disorders",
        "qualifications": ["MBBS", "MD in Dermatology"],
        "experience_importance": "Moderate"
    },
    "Psychiatrist": {
        "description": "Specialist in mental health disorders",
        "qualifications": ["MBBS", "MD in Psychiatry"],
        "experience_importance": "High"
    },
    "Orthopedic Surgeon": {
        "description": "Specialist in bone and joint disorders",
        "qualifications": ["MBBS", "MS/MCh in Orthopedics"],
        "experience_importance": "High"
    },
    "Infectious Disease Specialist": {
        "description": "Specialist in infectious and communicable diseases",
        "qualifications": ["MBBS", "MD in General Medicine", "Super-specialty"],
        "experience_importance": "Very High"
    }
}


def specialist_recommendation_node(llm_model):
    """
    Specialist Recommendation Agent
    - Maps predicted diseases to appropriate specialists
    - Ranks specialists by priority
    - Explains recommendations
    """
    
    def node(state):
        system_prompt = f"""
        You are a medical routing system that recommends appropriate specialists based on diagnoses.
        
        Your role is to:
        1. Analyze the predicted diseases from medical reasoning
        2. Map diseases to appropriate specialists
        3. Rank specialists by relevance and priority
        4. Provide clear justification for recommendations
        
        Disease to Specialist Mapping:
        {json.dumps(DISEASE_SPECIALIST_MAP, indent=2)}
        
        Specialist Information:
        {json.dumps(SPECIALIST_INFO, indent=2)}
        
        Guidelines:
        - For mild conditions, general physician is often sufficient
        - For complex/serious conditions, recommend super-specialists
        - Consider combination of diseases when recommending
        - Primary specialist should be most relevant for chief complaint
        - Always include General Physician as fallback option
        - Rank by urgency and relevance
        """
        
        prompt = ChatPromptTemplate.from_messages([
            ("system", system_prompt),
            ("placeholder", "{messages}"),
        ])
        
        agent = create_agent(
            model=llm_model.with_structured_output(SpecialistRecommendationOutput),
            tools=[],
            prompt=prompt,
        )
        
        result = agent.invoke(state)
        
        recommendation_output = result.get("specialist_recommendation", {})
        
        # Build response
        specialists_list = recommendation_output.get("specialists", [])
        justifications = recommendation_output.get("justifications", {})
        primary = recommendation_output.get("primary_specialist", "General Physician")
        
        response_text = f"""
SPECIALIST RECOMMENDATIONS:

🎯 Primary Recommended Specialist: {primary}

Recommended Specialists (in order of priority):
"""
        
        for i, specialist in enumerate(specialists_list, 1):
            justification = justifications.get(specialist, "")
            info = SPECIALIST_INFO.get(specialist, {})
            response_text += f"""
{i}. {specialist}
   Description: {info.get('description', '')}
   Justification: {justification}
   Qualifications: {', '.join(info.get('qualifications', []))}
"""
        
        response_text += f"""

📋 Next Steps:
1. Search for {primary} in your area
2. Check their availability and fees
3. Book an appointment at your preferred time
4. Provide medical history during consultation

⚠️ Remember: This is AI-generated guidance. The final diagnosis and treatment 
will be determined by the actual specialist during consultation.
        """
        
        # Log interaction
        from ..database.crud import InteractionLogCRUD
        try:
            InteractionLogCRUD.log_interaction({
                "user_id": state.get("user_id", "unknown"),
                "interaction_type": "SPECIALIST_RECOMMENDATION",
                "specialist_recommended": primary
            })
        except:
            pass
        
        return Command(
            update={
                "messages": state["messages"] + [AIMessage(content=response_text)],
                "current_reasoning": f"Specialist Recommendation: Primary = {primary}",
                "recommended_specialists": specialists_list,
                "primary_specialist": primary,
                "specialist_justifications": justifications
            },
            goto="supervisor"
        )
    
    return node

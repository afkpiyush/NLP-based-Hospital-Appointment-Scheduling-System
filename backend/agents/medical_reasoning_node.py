"""
Medical Reasoning Agent Node
AI-powered disease prediction using symptom analysis
"""
from langgraph.types import Command
from langchain_core.messages import AIMessage
from langchain_core.prompts.chat import ChatPromptTemplate
from langchain.agents import create_agent
from pydantic import BaseModel, Field
from typing import List, Dict, Any
import json


class DiseasePrediction(BaseModel):
    """Disease prediction output"""
    disease_name: str = Field(..., description="Name of the predicted disease")
    confidence: float = Field(..., ge=0, le=1, description="Confidence score (0-1)")
    description: str = Field(..., description="Brief description of the disease")
    risk_factors: List[str] = Field(default=[], description="Associated risk factors")
    recommended_tests: List[str] = Field(default=[], description="Recommended medical tests")


class MedicalReasoningOutput(BaseModel):
    """Structured output for medical reasoning"""
    predicted_diseases: List[DiseasePrediction] = Field(..., description="Top 3 predicted diseases")
    disclaimer: str = Field(
        default="⚠️ MEDICAL DISCLAIMER: This is an AI analysis for informational purposes only and is NOT a medical diagnosis. "
                "Please consult a qualified healthcare professional for proper diagnosis and treatment.",
        description="Medical disclaimer"
    )
    needs_emergency: bool = Field(default=False, description="Whether emergency care is needed")
    emergency_reason: str = Field(default="", description="Reason for emergency recommendation if applicable")


# Medical knowledge base (simplified)
DISEASE_SYMPTOM_MAP = {
    "Common Cold": {
        "symptoms": ["cough", "runny nose", "sore throat", "sneezing"],
        "description": "Viral infection of upper respiratory tract",
        "risk_factors": ["exposure to sick person", "weakened immunity"],
        "tests": ["None typically needed"]
    },
    "Influenza (Flu)": {
        "symptoms": ["fever", "headache", "body aches", "cough", "fatigue"],
        "description": "Contagious respiratory illness caused by influenza virus",
        "risk_factors": ["seasonal exposure", "close contact with infected person"],
        "tests": ["Rapid flu test", "RT-PCR"]
    },
    "COVID-19": {
        "symptoms": ["fever", "cough", "shortness of breath", "loss of taste", "loss of smell"],
        "description": "Pandemic viral disease caused by SARS-CoV-2",
        "risk_factors": ["exposure to infected person", "travel"],
        "tests": ["RT-PCR", "Rapid antigen test", "Antibody test"]
    },
    "Bacterial Pneumonia": {
        "symptoms": ["fever", "cough", "shortness of breath", "chest pain", "body aches"],
        "description": "Lung infection caused by bacteria",
        "risk_factors": ["smoking", "weakened immunity", "recent respiratory infection"],
        "tests": ["Chest X-ray", "Blood culture"]
    },
    "Migraine": {
        "symptoms": ["headache", "nausea", "sensitivity to light", "visual disturbances"],
        "description": "Severe headache condition with neurological symptoms",
        "risk_factors": ["stress", "hormonal changes", "food triggers"],
        "tests": ["MRI", "CT scan (if first occurrence)"]
    },
    "Allergies": {
        "symptoms": ["sneezing", "runny nose", "itchy eyes", "skin rash"],
        "description": "Immune system reaction to foreign substances",
        "risk_factors": ["family history", "environmental exposure"],
        "tests": ["Allergy testing", "IgE levels"]
    },
    "Hypertension": {
        "symptoms": ["headache", "dizziness", "shortness of breath"],
        "description": "High blood pressure condition",
        "risk_factors": ["age", "obesity", "stress", "high salt intake"],
        "tests": ["Blood pressure monitoring", "ECG"]
    },
    "Diabetes": {
        "symptoms": ["excessive thirst", "frequent urination", "fatigue", "weight loss"],
        "description": "Metabolic disorder affecting blood sugar levels",
        "risk_factors": ["family history", "obesity", "sedentary lifestyle"],
        "tests": ["Fasting blood glucose", "HbA1c", "Oral glucose tolerance test"]
    },
    "Anxiety Disorder": {
        "symptoms": ["chest pain", "shortness of breath", "dizziness", "panic attacks"],
        "description": "Mental health condition characterized by excessive worry",
        "risk_factors": ["stress", "trauma", "genetic predisposition"],
        "tests": ["Psychiatric evaluation"]
    },
    "Gastritis": {
        "symptoms": ["abdominal pain", "nausea", "vomiting", "loss of appetite"],
        "description": "Inflammation of stomach lining",
        "risk_factors": ["H. pylori infection", "NSAIDs", "stress"],
        "tests": ["Endoscopy", "H. pylori test"]
    }
}

# Emergency symptoms that require immediate care
EMERGENCY_SYMPTOMS = [
    "difficulty breathing",
    "chest pain",
    "severe bleeding",
    "unconsciousness",
    "severe dizziness",
    "loss of consciousness",
    "severe allergic reaction",
    "poisoning",
    "choking",
    "severe burns"
]


def medical_reasoning_node(llm_model):
    """
    Medical Reasoning Agent
    - Analyzes extracted symptoms
    - Predicts likely diseases using medical KB
    - Returns top 3 diseases with confidence scores
    - Includes medical disclaimer
    """
    
    def node(state):
        system_prompt = f"""
        You are an AI medical reasoning system trained on clinical knowledge.
        
        Your role is to:
        1. Analyze the patient's symptoms
        2. Cross-reference with medical knowledge base
        3. Predict top 3 possible diseases with confidence scores
        4. Explain reasoning for each prediction
        5. Always include appropriate medical disclaimers
        
        Known Diseases Database:
        {json.dumps(DISEASE_SYMPTOM_MAP, indent=2)}
        
        Important Guidelines:
        - Base predictions on symptom overlap
        - Consider symptom severity and duration
        - Flag if emergency symptoms are present
        - Provide confidence scores (0.0-1.0) for each prediction
        - Include relevant medical tests that might help confirm diagnosis
        - NEVER provide treatment recommendations
        - Always emphasize need for professional medical consultation
        
        If symptoms suggest emergency condition (see list below), flag urgently.
        Emergency Symptoms: {', '.join(EMERGENCY_SYMPTOMS)}
        """
        
        prompt = ChatPromptTemplate.from_messages([
            ("system", system_prompt),
            ("placeholder", "{messages}"),
        ])
        
        # Create agent
        agent = create_agent(
            model=llm_model.with_structured_output(MedicalReasoningOutput),
            tools=[],
            prompt=prompt,
        )
        
        result = agent.invoke(state)
        
        # Extract reasoning output
        reasoning_output = result.get("reasoning", {})
        
        # Build response with medical disclaimer
        disclaimer = reasoning_output.get("disclaimer", "")
        
        # Format disease predictions
        diseases_text = "PREDICTED CONDITIONS (AI Analysis Only):\n"
        predictions = reasoning_output.get("predicted_diseases", [])
        
        for i, disease in enumerate(predictions, 1):
            if isinstance(disease, dict):
                diseases_text += f"""
{i}. {disease.get('disease_name', 'Unknown')}
   Confidence: {disease.get('confidence', 0):.1%}
   Description: {disease.get('description', '')}
   Risk Factors: {', '.join(disease.get('risk_factors', []))}
   Recommended Tests: {', '.join(disease.get('recommended_tests', []))}
"""
        
        # Check for emergency
        emergency_alert = ""
        if reasoning_output.get("needs_emergency"):
            emergency_alert = f"\n🚨 EMERGENCY ALERT: {reasoning_output.get('emergency_reason', 'Seek immediate medical attention!')}\n"
        
        response_text = f"""
{emergency_alert}
{diseases_text}

{disclaimer}
        """
        
        # Log interaction
        from ..database.crud import InteractionLogCRUD
        try:
            predicted_diseases = [d.get('disease_name', '') for d in predictions if isinstance(d, dict)]
            InteractionLogCRUD.log_interaction({
                "user_id": state.get("user_id", "unknown"),
                "interaction_type": "DIAGNOSIS",
                "diseases_predicted": predicted_diseases
            })
        except:
            pass
        
        return Command(
            update={
                "messages": state["messages"] + [AIMessage(content=response_text)],
                "current_reasoning": f"Medical Reasoning: {len(predictions)} diseases predicted",
                "predicted_diseases": predictions,
                "needs_emergency": reasoning_output.get("needs_emergency", False)
            },
            goto="supervisor"
        )
    
    return node

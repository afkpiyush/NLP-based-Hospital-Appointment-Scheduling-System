"""
Chat Conversation Agent Node
Manages post-appointment doctor-patient messaging
"""
from langgraph.types import Command
from langchain_core.messages import AIMessage
from langchain_core.prompts.chat import ChatPromptTemplate
from langchain.agents import create_agent, tool
from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime


class ChatMessageData(BaseModel):
    """Chat message structure"""
    sender_type: str = Field(..., description="USER or DOCTOR")
    sender_id: str
    content: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    is_moderated: bool = False
    language: str = "EN"


class ChatConversationOutput(BaseModel):
    """Chat conversation output"""
    message_acknowledged: bool
    message_id: str
    chat_updated: bool
    notification_sent: bool


# Content moderation keywords (basic)
FLAGGED_KEYWORDS = [
    "prescription for anyone",
    "controlled substances",
    "without examination",
    "self-diagnosis",
    "harmful advice"
]


@tool
def store_chat_message(
    chat_id: str,
    sender_type: str,
    sender_id: str,
    content: str,
    language: str = "EN"
) -> str:
    """
    Store chat message in database
    """
    from ..database.crud import ChatCRUD
    
    try:
        # Basic content moderation
        is_flagged = any(keyword.lower() in content.lower() for keyword in FLAGGED_KEYWORDS)
        
        message_data = {
            "sender_type": sender_type,
            "sender_id": sender_id,
            "content": content,
            "is_moderated": is_flagged,
            "language": language,
            "timestamp": datetime.utcnow()
        }
        
        success = ChatCRUD.add_message(chat_id, message_data)
        
        if is_flagged:
            return f"Message stored but flagged for moderation"
        else:
            return f"Message stored successfully"
    except Exception as e:
        return f"Error storing message: {str(e)}"


@tool
def get_chat_history(chat_id: str, limit: int = 20) -> str:
    """
    Retrieve chat history
    """
    from ..database.crud import ChatCRUD
    
    try:
        messages = ChatCRUD.get_messages(chat_id, limit)
        
        if not messages:
            return "No messages in this conversation yet"
        
        history_text = "Chat History (recent messages):\n"
        for msg in messages:
            sender = "You" if msg.get("sender_type") == "USER" else "Doctor"
            time_str = msg.get("timestamp", "")
            history_text += f"\n{sender} ({time_str}):\n{msg.get('content', '')}\n"
        
        return history_text
    except Exception as e:
        return f"Error retrieving chat history: {str(e)}"


@tool
def moderate_message(content: str) -> str:
    """
    Check message for potentially problematic content
    """
    issues = []
    
    # Check for prescription requests
    if any(word in content.lower() for word in ["prescribe", "give me", "medication for"]):
        issues.append("Prescription discussion detected")
    
    # Check for diagnosis requests
    if any(word in content.lower() for word in ["do i have", "am i", "my condition is"]):
        issues.append("Diagnosis seeking detected")
    
    # Check content length
    if len(content) > 5000:
        issues.append("Message too long")
    
    if issues:
        return f"Issues detected: {', '.join(issues)}"
    else:
        return "Message content appropriate"


def chat_conversation_node(llm_model):
    """
    Chat Conversation Agent
    - Manages doctor-patient messaging after appointment
    - Stores messages securely
    - Performs content moderation
    - Maintains conversation context
    """
    
    def node(state):
        system_prompt = """
        You are a medical chat coordinator for post-appointment communication.
        
        Your role is to:
        1. Facilitate communication between doctor and patient
        2. Ensure message appropriateness
        3. Maintain professional medical standards
        4. Handle technical aspects of chat management
        
        Guidelines:
        - Ensure conversations remain professional
        - Flag inappropriate content for review
        - Maintain patient privacy
        - Store all communications securely
        - Notify parties of new messages
        
        Remember: This is for follow-up communication only.
        Emergency medical issues should be directed to hospital.
        """
        
        prompt = ChatPromptTemplate.from_messages([
            ("system", system_prompt),
            ("placeholder", "{messages}"),
        ])
        
        # Create agent with tools
        agent = create_agent(
            model=llm_model,
            tools=[
                store_chat_message,
                get_chat_history,
                moderate_message
            ],
            prompt=prompt,
        )
        
        result = agent.invoke(state)
        
        # Process result
        final_message = result.get("messages", [])
        if final_message:
            last_message = final_message[-1]
            response_text = last_message.content if hasattr(last_message, 'content') else str(last_message)
        else:
            response_text = "Chat processed"
        
        response_text += """

💬 CHAT UPDATED

Your message has been sent to the doctor.
The doctor will respond as soon as possible.

📌 Chat Guidelines:
- Be clear and concise
- Provide relevant medical history
- Don't share sensitive personal information
- For emergencies, call 911 or visit nearest hospital
        """
        
        return Command(
            update={
                "messages": state["messages"] + [AIMessage(content=response_text)],
                "current_reasoning": "Chat message processed"
            },
            goto="supervisor"
        )
    
    return node

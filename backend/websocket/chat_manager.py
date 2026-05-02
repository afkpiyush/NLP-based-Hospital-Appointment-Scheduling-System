"""
WebSocket Chat Manager
Handles real-time bidirectional communication between doctors and patients
Uses WebSockets for low-latency messaging
"""
import asyncio
import json
import logging
from typing import Dict, List, Set
from datetime import datetime
from fastapi import WebSocket, WebSocketDisconnect
from ..database.crud import ChatCRUD
from ..services.translation import get_translation_service

logger = logging.getLogger(__name__)


class ChatConnectionManager:
    """
    Manages WebSocket connections for chat
    Handles multiple concurrent chat sessions
    Routes messages between doctor and patient
    """
    
    def __init__(self):
        """Initialize connection manager"""
        # Map: chat_id -> {user_connections, doctor_connections}
        self.active_connections: Dict[str, Dict[str, List[WebSocket]]] = {}
        self.translation_service = get_translation_service()
    
    async def connect(self, 
                     websocket: WebSocket, 
                     chat_id: str, 
                     user_id: str,
                     user_type: str = "USER"):
        """
        Handle new WebSocket connection
        
        Args:
            websocket: WebSocket connection
            chat_id: Chat session ID
            user_id: User/Doctor ID
            user_type: USER or DOCTOR
        """
        await websocket.accept()
        
        # Initialize chat room if not exists
        if chat_id not in self.active_connections:
            self.active_connections[chat_id] = {
                "users": [],
                "doctors": []
            }
        
        # Store connection
        connection_key = "doctors" if user_type == "DOCTOR" else "users"
        self.active_connections[chat_id][connection_key].append(websocket)
        
        logger.info(f"Client {user_id} ({user_type}) connected to chat {chat_id}")
        
        # Notify others that user is online
        await self._notify_status(chat_id, user_type, "online", user_id)
    
    async def disconnect(self, websocket: WebSocket, chat_id: str, user_id: str, user_type: str = "USER"):
        """
        Handle WebSocket disconnection
        """
        if chat_id not in self.active_connections:
            return
        
        connection_key = "doctors" if user_type == "DOCTOR" else "users"
        
        # Remove this specific connection
        self.active_connections[chat_id][connection_key] = [
            ws for ws in self.active_connections[chat_id][connection_key] if ws != websocket
        ]
        
        logger.info(f"Client {user_id} ({user_type}) disconnected from chat {chat_id}")
        
        # Notify others that user is offline
        await self._notify_status(chat_id, user_type, "offline", user_id)
        
        # Clean up empty chat room
        if (not self.active_connections[chat_id]["users"] and 
            not self.active_connections[chat_id]["doctors"]):
            del self.active_connections[chat_id]
    
    async def broadcast_message(self,
                               chat_id: str,
                               sender_type: str,
                               sender_id: str,
                               message_data: Dict) -> bool:
        """
        Broadcast message to both parties in chat
        
        Args:
            chat_id: Chat session ID
            sender_type: USER or DOCTOR
            sender_id: ID of sender
            message_data: Message content and metadata
            
        Returns:
            Success flag
        """
        if chat_id not in self.active_connections:
            return False
        
        try:
            # Store message in database
            ChatCRUD.add_message(chat_id, {
                "sender_type": sender_type,
                "sender_id": sender_id,
                "content": message_data.get("content", ""),
                "language": message_data.get("language", "EN"),
                "timestamp": datetime.utcnow()
            })
            
            # Prepare broadcast message
            broadcast_msg = {
                "type": "message",
                "sender_type": sender_type,
                "sender_id": sender_id,
                "content": message_data.get("content"),
                "timestamp": datetime.utcnow().isoformat(),
                "language": message_data.get("language", "EN")
            }
            
            # Broadcast to recipients
            recipient_type = "DOCTOR" if sender_type == "USER" else "USER"
            recipient_key = "doctors" if recipient_type == "DOCTOR" else "users"
            
            if self.active_connections[chat_id][recipient_key]:
                for connection in self.active_connections[chat_id][recipient_key]:
                    try:
                        await connection.send_json(broadcast_msg)
                    except Exception as e:
                        logger.error(f"Error broadcasting message: {e}")
            
            return True
        except Exception as e:
            logger.error(f"Error in broadcast_message: {e}")
            return False
    
    async def send_typing_indicator(self, 
                                   chat_id: str,
                                   sender_type: str,
                                   sender_id: str):
        """Send typing indicator to other party"""
        if chat_id not in self.active_connections:
            return
        
        typing_msg = {
            "type": "typing",
            "sender_id": sender_id,
            "sender_type": sender_type
        }
        
        recipient_type = "DOCTOR" if sender_type == "USER" else "USER"
        recipient_key = "doctors" if recipient_type == "DOCTOR" else "users"
        
        for connection in self.active_connections[chat_id][recipient_key]:
            try:
                await connection.send_json(typing_msg)
            except:
                pass
    
    async def send_read_receipt(self,
                               chat_id: str,
                               user_type: str,
                               user_id: str):
        """Send read receipt to other party"""
        if chat_id not in self.active_connections:
            return
        
        read_msg = {
            "type": "read",
            "user_id": user_id,
            "user_type": user_type,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        recipient_type = "DOCTOR" if user_type == "USER" else "USER"
        recipient_key = "doctors" if recipient_type == "DOCTOR" else "users"
        
        for connection in self.active_connections[chat_id][recipient_key]:
            try:
                await connection.send_json(read_msg)
            except:
                pass
    
    async def _notify_status(self,
                            chat_id: str,
                            user_type: str,
                            status: str,
                            user_id: str):
        """Notify other party of status change (online/offline)"""
        if chat_id not in self.active_connections:
            return
        
        status_msg = {
            "type": "status",
            "user_type": user_type,
            "user_id": user_id,
            "status": status,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        recipient_type = "DOCTOR" if user_type == "USER" else "USER"
        recipient_key = "doctors" if recipient_type == "DOCTOR" else "users"
        
        for connection in self.active_connections[chat_id][recipient_key]:
            try:
                await connection.send_json(status_msg)
            except:
                pass
    
    def get_active_users_count(self, chat_id: str) -> Dict[str, int]:
        """Get count of active users in a chat"""
        if chat_id not in self.active_connections:
            return {"users": 0, "doctors": 0}
        
        return {
            "users": len(self.active_connections[chat_id]["users"]),
            "doctors": len(self.active_connections[chat_id]["doctors"])
        }


# Global connection manager instance
chat_manager = ChatConnectionManager()


async def handle_chat_connection(
    websocket: WebSocket,
    chat_id: str,
    user_id: str,
    user_type: str = "USER"
):
    """
    Handle a WebSocket chat connection lifecycle
    
    Message Format:
    {
        "type": "message|typing|read",
        "content": "...",  # for message type
        "language": "EN"
    }
    """
    
    await chat_manager.connect(websocket, chat_id, user_id, user_type)
    
    try:
        while True:
            # Receive message from client
            data = await websocket.receive_text()
            message = json.loads(data)
            
            msg_type = message.get("type", "message")
            
            if msg_type == "message":
                # Handle regular message
                await chat_manager.broadcast_message(
                    chat_id,
                    user_type,
                    user_id,
                    message
                )
            
            elif msg_type == "typing":
                # Handle typing indicator
                await chat_manager.send_typing_indicator(
                    chat_id,
                    user_type,
                    user_id
                )
            
            elif msg_type == "read":
                # Handle read receipt
                await chat_manager.send_read_receipt(
                    chat_id,
                    user_type,
                    user_id
                )
            
    except WebSocketDisconnect:
        await chat_manager.disconnect(websocket, chat_id, user_id, user_type)
    except Exception as e:
        logger.error(f"Chat connection error: {e}")
        await chat_manager.disconnect(websocket, chat_id, user_id, user_type)


class ChatMessageQueue:
    """
    Queue for managing chat messages (useful for message delivery guarantees)
    Can be enhanced with Redis for distributed systems
    """
    
    def __init__(self):
        self.queues: Dict[str, asyncio.Queue] = {}
    
    async def enqueue(self, chat_id: str, message: Dict):
        """Add message to queue"""
        if chat_id not in self.queues:
            self.queues[chat_id] = asyncio.Queue()
        
        await self.queues[chat_id].put(message)
    
    async def dequeue(self, chat_id: str) -> Dict:
        """Get message from queue"""
        if chat_id not in self.queues:
            self.queues[chat_id] = asyncio.Queue()
        
        return await self.queues[chat_id].get()
    
    def get_queue_size(self, chat_id: str) -> int:
        """Get pending message count"""
        if chat_id not in self.queues:
            return 0
        return self.queues[chat_id].qsize()


# Global message queue
message_queue = ChatMessageQueue()

"""
CRUD operations for database
Supports both MongoDB and PostgreSQL
"""
from typing import List, Optional, Dict, Any
from datetime import datetime
from .connection import get_db_collection, DatabaseConfig
from ..models.schemas import User, Doctor, Appointment, ChatHistory, MedicalInteractionLog
import uuid


# ============== USER OPERATIONS ==============

class UserCRUD:
    """User database operations"""
    
    COLLECTION_NAME = "users"
    
    @staticmethod
    def create_user(user_data: Dict[str, Any]) -> str:
        """Create new user, return user_id"""
        if DatabaseConfig.DB_TYPE == "mongodb":
            collection = get_db_collection(UserCRUD.COLLECTION_NAME)
            user_data["user_id"] = str(uuid.uuid4())
            user_data["created_at"] = datetime.utcnow()
            user_data["is_active"] = True
            result = collection.insert_one(user_data)
            return user_data["user_id"]
        # PostgreSQL implementation would follow similar pattern
    
    @staticmethod
    def get_user(user_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve user by ID"""
        if DatabaseConfig.DB_TYPE == "mongodb":
            collection = get_db_collection(UserCRUD.COLLECTION_NAME)
            return collection.find_one({"user_id": user_id})
    
    @staticmethod
    def get_user_by_email(email: str) -> Optional[Dict[str, Any]]:
        """Retrieve user by email"""
        if DatabaseConfig.DB_TYPE == "mongodb":
            collection = get_db_collection(UserCRUD.COLLECTION_NAME)
            return collection.find_one({"email": email})
    
    @staticmethod
    def update_user(user_id: str, update_data: Dict[str, Any]) -> bool:
        """Update user information"""
        if DatabaseConfig.DB_TYPE == "mongodb":
            collection = get_db_collection(UserCRUD.COLLECTION_NAME)
            result = collection.update_one(
                {"user_id": user_id},
                {"$set": {**update_data, "last_login": datetime.utcnow()}}
            )
            return result.modified_count > 0
    
    @staticmethod
    def delete_user(user_id: str) -> bool:
        """Soft delete user (mark as inactive)"""
        if DatabaseConfig.DB_TYPE == "mongodb":
            collection = get_db_collection(UserCRUD.COLLECTION_NAME)
            result = collection.update_one(
                {"user_id": user_id},
                {"$set": {"is_active": False}}
            )
            return result.modified_count > 0
    
    @staticmethod
    def get_users_by_location(latitude: float, longitude: float, radius_km: float = 50) -> List[Dict]:
        """Get users within radius (for notifications, etc.)"""
        if DatabaseConfig.DB_TYPE == "mongodb":
            collection = get_db_collection(UserCRUD.COLLECTION_NAME)
            # MongoDB geospatial query
            results = collection.find({
                "location": {
                    "$near": {
                        "$geometry": {
                            "type": "Point",
                            "coordinates": [longitude, latitude]
                        },
                        "$maxDistance": radius_km * 1000
                    }
                }
            })
            return list(results)


# ============== DOCTOR OPERATIONS ==============

class DoctorCRUD:
    """Doctor database operations"""
    
    COLLECTION_NAME = "doctors"
    
    @staticmethod
    def create_doctor(doctor_data: Dict[str, Any]) -> str:
        """Create new doctor, return doctor_id"""
        if DatabaseConfig.DB_TYPE == "mongodb":
            collection = get_db_collection(DoctorCRUD.COLLECTION_NAME)
            doctor_data["doctor_id"] = str(uuid.uuid4())
            doctor_data["created_at"] = datetime.utcnow()
            doctor_data["rating"] = 0.0
            result = collection.insert_one(doctor_data)
            return doctor_data["doctor_id"]
    
    @staticmethod
    def get_doctor(doctor_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve doctor by ID"""
        if DatabaseConfig.DB_TYPE == "mongodb":
            collection = get_db_collection(DoctorCRUD.COLLECTION_NAME)
            return collection.find_one({"doctor_id": doctor_id})
    
    @staticmethod
    def search_doctors_by_specialization(
        specialization: str,
        latitude: float,
        longitude: float,
        max_distance_km: float = 50
    ) -> List[Dict[str, Any]]:
        """Search doctors by specialization and location"""
        if DatabaseConfig.DB_TYPE == "mongodb":
            collection = get_db_collection(DoctorCRUD.COLLECTION_NAME)
            results = collection.find({
                "specialization": {"$regex": specialization, "$options": "i"},
                "clinic_location": {
                    "$near": {
                        "$geometry": {
                            "type": "Point",
                            "coordinates": [longitude, latitude]
                        },
                        "$maxDistance": max_distance_km * 1000
                    }
                }
            }).sort("rating", -1)
            return list(results)
    
    @staticmethod
    def get_doctors_by_specialization(specialization: str) -> List[Dict[str, Any]]:
        """Get all doctors with specific specialization"""
        if DatabaseConfig.DB_TYPE == "mongodb":
            collection = get_db_collection(DoctorCRUD.COLLECTION_NAME)
            results = collection.find({
                "specialization": {"$regex": specialization, "$options": "i"}
            }).sort("rating", -1)
            return list(results)
    
    @staticmethod
    def update_doctor_availability(doctor_id: str, new_slots: List[Dict]) -> bool:
        """Update doctor's availability slots"""
        if DatabaseConfig.DB_TYPE == "mongodb":
            collection = get_db_collection(DoctorCRUD.COLLECTION_NAME)
            result = collection.update_one(
                {"doctor_id": doctor_id},
                {"$set": {"availability_slots": new_slots}}
            )
            return result.modified_count > 0
    
    @staticmethod
    def mark_slot_booked(doctor_id: str, slot_date: str, slot_time: str, user_id: str) -> bool:
        """Mark a specific time slot as booked"""
        if DatabaseConfig.DB_TYPE == "mongodb":
            collection = get_db_collection(DoctorCRUD.COLLECTION_NAME)
            result = collection.update_one(
                {
                    "doctor_id": doctor_id,
                    "availability_slots.date": slot_date,
                    "availability_slots.start_time": slot_time
                },
                {
                    "$set": {
                        "availability_slots.$.is_available": False,
                        "availability_slots.$.booked_by": user_id
                    }
                }
            )
            return result.modified_count > 0
    
    @staticmethod
    def update_doctor_rating(doctor_id: str, new_rating: float) -> bool:
        """Update doctor's average rating"""
        if DatabaseConfig.DB_TYPE == "mongodb":
            collection = get_db_collection(DoctorCRUD.COLLECTION_NAME)
            result = collection.update_one(
                {"doctor_id": doctor_id},
                {"$set": {"rating": new_rating}}
            )
            return result.modified_count > 0


# ============== APPOINTMENT OPERATIONS ==============

class AppointmentCRUD:
    """Appointment database operations"""
    
    COLLECTION_NAME = "appointments"
    
    @staticmethod
    def create_appointment(appointment_data: Dict[str, Any]) -> str:
        """Create new appointment, return appointment_id"""
        if DatabaseConfig.DB_TYPE == "mongodb":
            collection = get_db_collection(AppointmentCRUD.COLLECTION_NAME)
            appointment_data["appointment_id"] = str(uuid.uuid4())
            appointment_data["created_at"] = datetime.utcnow()
            appointment_data["status"] = "BOOKED"
            result = collection.insert_one(appointment_data)
            return appointment_data["appointment_id"]
    
    @staticmethod
    def get_appointment(appointment_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve appointment by ID"""
        if DatabaseConfig.DB_TYPE == "mongodb":
            collection = get_db_collection(AppointmentCRUD.COLLECTION_NAME)
            return collection.find_one({"appointment_id": appointment_id})
    
    @staticmethod
    def get_user_appointments(user_id: str, status: Optional[str] = None) -> List[Dict]:
        """Get all appointments for a user"""
        if DatabaseConfig.DB_TYPE == "mongodb":
            collection = get_db_collection(AppointmentCRUD.COLLECTION_NAME)
            query = {"user_id": user_id}
            if status:
                query["status"] = status
            results = collection.find(query).sort("appointment_date", -1)
            return list(results)
    
    @staticmethod
    def get_doctor_appointments(doctor_id: str, date: Optional[str] = None) -> List[Dict]:
        """Get appointments for a doctor"""
        if DatabaseConfig.DB_TYPE == "mongodb":
            collection = get_db_collection(AppointmentCRUD.COLLECTION_NAME)
            query = {"doctor_id": doctor_id}
            if date:
                query["appointment_date"] = {"$regex": f"^{date}"}
            results = collection.find(query).sort("appointment_date", 1)
            return list(results)
    
    @staticmethod
    def update_appointment(appointment_id: str, update_data: Dict[str, Any]) -> bool:
        """Update appointment details"""
        if DatabaseConfig.DB_TYPE == "mongodb":
            collection = get_db_collection(AppointmentCRUD.COLLECTION_NAME)
            result = collection.update_one(
                {"appointment_id": appointment_id},
                {"$set": update_data}
            )
            return result.modified_count > 0
    
    @staticmethod
    def cancel_appointment(appointment_id: str) -> bool:
        """Cancel appointment"""
        if DatabaseConfig.DB_TYPE == "mongodb":
            collection = get_db_collection(AppointmentCRUD.COLLECTION_NAME)
            result = collection.update_one(
                {"appointment_id": appointment_id},
                {
                    "$set": {
                        "status": "CANCELLED",
                        "cancelled_at": datetime.utcnow()
                    }
                }
            )
            return result.modified_count > 0
    
    @staticmethod
    def mark_appointment_completed(appointment_id: str, doctor_notes: str = "") -> bool:
        """Mark appointment as completed"""
        if DatabaseConfig.DB_TYPE == "mongodb":
            collection = get_db_collection(AppointmentCRUD.COLLECTION_NAME)
            result = collection.update_one(
                {"appointment_id": appointment_id},
                {
                    "$set": {
                        "status": "COMPLETED",
                        "completed_at": datetime.utcnow(),
                        "doctor_notes": doctor_notes
                    }
                }
            )
            return result.modified_count > 0


# ============== CHAT OPERATIONS ==============

class ChatCRUD:
    """Chat history database operations"""
    
    COLLECTION_NAME = "chat_history"
    
    @staticmethod
    def create_chat_session(appointment_id: str, user_id: str, doctor_id: str) -> str:
        """Create new chat session, return chat_id"""
        if DatabaseConfig.DB_TYPE == "mongodb":
            collection = get_db_collection(ChatCRUD.COLLECTION_NAME)
            chat_data = {
                "chat_id": str(uuid.uuid4()),
                "appointment_id": appointment_id,
                "user_id": user_id,
                "doctor_id": doctor_id,
                "messages": [],
                "created_at": datetime.utcnow(),
                "last_message_at": None,
                "is_active": True
            }
            result = collection.insert_one(chat_data)
            return chat_data["chat_id"]
    
    @staticmethod
    def get_chat_history(chat_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve chat history"""
        if DatabaseConfig.DB_TYPE == "mongodb":
            collection = get_db_collection(ChatCRUD.COLLECTION_NAME)
            return collection.find_one({"chat_id": chat_id})
    
    @staticmethod
    def get_chat_by_appointment(appointment_id: str) -> Optional[Dict[str, Any]]:
        """Get chat by appointment ID"""
        if DatabaseConfig.DB_TYPE == "mongodb":
            collection = get_db_collection(ChatCRUD.COLLECTION_NAME)
            return collection.find_one({"appointment_id": appointment_id})
    
    @staticmethod
    def add_message(chat_id: str, message_data: Dict[str, Any]) -> bool:
        """Add message to chat"""
        if DatabaseConfig.DB_TYPE == "mongodb":
            collection = get_db_collection(ChatCRUD.COLLECTION_NAME)
            message_data["timestamp"] = datetime.utcnow()
            result = collection.update_one(
                {"chat_id": chat_id},
                {
                    "$push": {"messages": message_data},
                    "$set": {"last_message_at": datetime.utcnow()}
                }
            )
            return result.modified_count > 0
    
    @staticmethod
    def get_messages(chat_id: str, limit: int = 50) -> List[Dict]:
        """Get messages from chat (latest N messages)"""
        if DatabaseConfig.DB_TYPE == "mongodb":
            collection = get_db_collection(ChatCRUD.COLLECTION_NAME)
            chat = collection.find_one({"chat_id": chat_id})
            if chat:
                return chat["messages"][-limit:]
            return []
    
    @staticmethod
    def close_chat(chat_id: str) -> bool:
        """Close chat session"""
        if DatabaseConfig.DB_TYPE == "mongodb":
            collection = get_db_collection(ChatCRUD.COLLECTION_NAME)
            result = collection.update_one(
                {"chat_id": chat_id},
                {"$set": {"is_active": False}}
            )
            return result.modified_count > 0


# ============== MEDICAL INTERACTION LOG OPERATIONS ==============

class InteractionLogCRUD:
    """Medical interaction logging"""
    
    COLLECTION_NAME = "medical_interaction_logs"
    
    @staticmethod
    def log_interaction(log_data: Dict[str, Any]) -> str:
        """Log medical interaction"""
        if DatabaseConfig.DB_TYPE == "mongodb":
            collection = get_db_collection(InteractionLogCRUD.COLLECTION_NAME)
            log_data["log_id"] = str(uuid.uuid4())
            log_data["created_at"] = datetime.utcnow()
            result = collection.insert_one(log_data)
            return log_data["log_id"]
    
    @staticmethod
    def get_user_interaction_history(user_id: str, limit: int = 100) -> List[Dict]:
        """Get interaction history for user"""
        if DatabaseConfig.DB_TYPE == "mongodb":
            collection = get_db_collection(InteractionLogCRUD.COLLECTION_NAME)
            results = collection.find({"user_id": user_id}).sort("created_at", -1).limit(limit)
            return list(results)
    
    @staticmethod
    def get_interactions_by_type(interaction_type: str) -> List[Dict]:
        """Get all interactions of specific type"""
        if DatabaseConfig.DB_TYPE == "mongodb":
            collection = get_db_collection(InteractionLogCRUD.COLLECTION_NAME)
            results = collection.find({"interaction_type": interaction_type}).sort("created_at", -1)
            return list(results)

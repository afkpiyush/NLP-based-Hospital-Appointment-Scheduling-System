"""
Test suite for Healthcare Assistant Workflow
"""
import asyncio
import sys
import os

# Add the project root to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from backend.agents.workflow import get_workflow
from unittest.mock import patch, MagicMock

# Mock the database CRUD operations to allow testing without a live database
mock_crud = MagicMock()
patch('backend.database.crud.UserCRUD', mock_crud).start()
patch('backend.database.crud.DoctorCRUD', mock_crud).start()
patch('backend.database.crud.AppointmentCRUD', mock_crud).start()
patch('backend.database.crud.ChatCRUD', mock_crud).start()
patch('backend.database.crud.InteractionLogCRUD', mock_crud).start()

# Mock Doctor search to return some dummy doctors
mock_crud.search_doctors_by_specialization.return_value = [
    {
        "doctor_id": "doc_001",
        "name": "Dr. Smith",
        "specialization": "Cardiologist",
        "rating": 4.5,
        "consultation_fee": 100,
        "clinic_location": {"latitude": 40.7128, "longitude": -74.0060}
    }
]
mock_crud.get_doctor.return_value = {
    "doctor_id": "doc_001",
    "name": "Dr. Smith",
    "availability_slots": [
        {"date": "2026-05-04", "start_time": "10:00", "is_available": True}
    ]
}

async def test_emergency_scenario():
    print("\n--- Testing Emergency Scenario ---")
    workflow = get_workflow()
    user_input = "I have severe chest pain and I can't breathe"
    user_id = "test_patient_001"
    
    result = await workflow.execute(user_input, user_id)
    
    print(f"User Query: {user_input}")
    print(f"Assistant Response: {result['messages'][-1]['content']}")
    print(f"Next Node: {result['next_node']}")
    
    # Assertions
    last_msg = result['messages'][-1]['content'].lower()
    assert "emergency" in last_msg or "911" in last_msg or "immediate" in last_msg
    print("✅ Emergency scenario test passed!")

async def test_symptom_analysis_flow():
    print("\n--- Testing Symptom Analysis Flow ---")
    workflow = get_workflow()
    user_input = "I've had a bad headache and nausea for two days"
    user_id = "test_patient_002"
    
    result = await workflow.execute(user_input, user_id)
    
    print(f"User Query: {user_input}")
    print(f"Assistant Response: {result['messages'][-1]['content']}")
    
    # Assertions
    last_msg = result['messages'][-1]['content'].lower()
    assert "headache" in last_msg or "condition" in last_msg or "specialist" in last_msg
    print("✅ Symptom analysis flow test passed!")

async def test_booking_intent():
    print("\n--- Testing Booking Intent ---")
    workflow = get_workflow()
    user_input = "I want to book an appointment with a cardiologist tomorrow"
    user_id = "test_patient_003"
    
    result = await workflow.execute(user_input, user_id)
    
    print(f"User Query: {user_input}")
    print(f"Assistant Response: {result['messages'][-1]['content']}")
    
    # Assertions
    last_msg = result['messages'][-1]['content'].lower()
    assert "book" in last_msg or "doctor" in last_msg or "appointment" in last_msg
    print("✅ Booking intent test passed!")

async def run_all_tests():
    print("Starting System Tests...")
    try:
        await test_emergency_scenario()
        await test_symptom_analysis_flow()
        await test_booking_intent()
        print("\n🎉 All tests completed successfully!")
    except Exception as e:
        print(f"\n❌ Tests failed: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(run_all_tests())

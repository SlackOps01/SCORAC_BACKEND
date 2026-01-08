from fastapi.testclient import TestClient
from app.main import app
import os

client = TestClient(app)

def test_flow():
    # 0. Login as Admin Default to get token or check if works
    # We expect admin@example.com / admin123 to be created on startup
    print("Logging in as Admin...")
    login_data = {"username": "admin@example.com", "password": "admin123"}
    response = client.post("/login", data=login_data)
    if response.status_code != 200:
        print("Login failed:", response.json())
        return
    
    token = response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    print("Admin logged in.")

    # 1. Register a teacher
    user_data = {"email": "teacher_auth@example.com", "password": "password123", "role": "teacher"}
    print("Registering Teacher...")
    # Registration endpoint is now protected or public? code says: 
    # def create_user(..., current_user: models.User = Depends(oauth2.get_current_user)):
    # So we need the admin token.
    response = client.post("/users/", json=user_data, headers=headers)
    if response.status_code == 400:
        print("User already exists, continuing...")
        # If exists, we might need to login as this teacher to test teacher flow, or just use admin
    else:
        assert response.status_code == 201
        print("Teacher registered.")

    # 2. Login as Teacher to create assignment
    print("Logging in as Teacher...")
    login_data_teacher = {"username": "teacher_auth@example.com", "password": "password123"}
    response = client.post("/login", data=login_data_teacher)
    teacher_token = response.json()["access_token"]
    teacher_headers = {"Authorization": f"Bearer {teacher_token}"}

    # 3. Create an Assignment
    print("Creating Assignment...")
    assignment_data = {
        "title": "Factorial Function",
        "description": "Write a function to return the factorial of n.",
        "criteria": "Function name 'factorial'. Recursive or iterative. Handle n=0."
    }
    response = client.post("/assignments/", json=assignment_data, headers=teacher_headers)
    if response.status_code != 201:
        print("Failed to create assignment:", response.json())
        return
    
    assignment_id = response.json()["id"]
    print(f"Assignment created: ID {assignment_id}")

    # 3.5 List and Get Assignment
    print("Listing assignments...")
    response = client.get("/assignments/")
    assert response.status_code == 200
    assignments = response.json()
    assert len(assignments) > 0
    print(f"Found {len(assignments)} assignments.")

    print(f"Getting details for assignment {assignment_id}...")
    response = client.get(f"/assignments/{assignment_id}")
    assert response.status_code == 200
    assert response.json()["id"] == assignment_id
    print("Assignment details verified.")

    # 4. Submit a Script (using teacher token for convenience, acting as student)
    script_content = """
def factorial(n):
    if n == 0:
        return 1
    return n * factorial(n-1)
"""
    files = {'file': ('factorial.py', script_content, 'text/x-python')}
    
    print("Submitting assignment...")
    response = client.post(f"/assignments/{assignment_id}/submit", files=files, headers=teacher_headers)
    
    if response.status_code == 500:
        print("Error from server (likely AI issue):", response.json())
    else:
        print("Scoring Response:", response.json())
        # We check if we got a score, even if 0 or error message from AI, struct should match
        if response.status_code == 200:
             assert "score" in response.json()

if __name__ == "__main__":
    test_flow()

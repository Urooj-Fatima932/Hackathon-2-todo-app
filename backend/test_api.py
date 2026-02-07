"""
Simple test script to verify the API is working.
"""
import requests
import json

BASE_URL = "http://localhost:8000"

def test_endpoints():
    """Test all API endpoints"""
    print("TEST Testing Todo API Endpoints\n")
    print("=" * 60)

    # Test 1: Root endpoint
    print("\n[1]  Testing GET /")
    try:
        response = requests.get(f"{BASE_URL}/")
        print(f"   Status: {response.status_code}")
        print(f"   Response: {response.json()}")
    except Exception as e:
        print(f"   ERROR: {e}")

    # Test 2: Health check
    print("\n[2]  Testing GET /health")
    try:
        response = requests.get(f"{BASE_URL}/health")
        print(f"   Status: {response.status_code}")
        print(f"   Response: {response.json()}")
    except Exception as e:
        print(f"   ERROR: {e}")

    # Test 3: Create a task
    print("\n[3]  Testing POST /api/test-user/tasks")
    task_data = {
        "title": "Complete Phase II hackathon",
        "description": "Build a full-stack todo app with authentication"
    }
    try:
        response = requests.post(
            f"{BASE_URL}/api/test-user/tasks",
            json=task_data
        )
        print(f"   Status: {response.status_code}")
        task = response.json()
        print(f"   Created Task ID: {task['id']}")
        print(f"   Title: {task['title']}")
        print(f"   Completed: {task['completed']}")
        task_id = task['id']
    except Exception as e:
        print(f"   ERROR: {e}")
        return

    # Test 4: List tasks
    print("\n[4]  Testing GET /api/test-user/tasks")
    try:
        response = requests.get(f"{BASE_URL}/api/test-user/tasks")
        print(f"   Status: {response.status_code}")
        data = response.json()
        print(f"   Total tasks: {data['total']}")
        for task in data['tasks']:
            print(f"   - [{task['id']}] {task['title']} (completed: {task['completed']})")
    except Exception as e:
        print(f"   ERROR: {e}")

    # Test 5: Get single task
    print(f"\n[5]  Testing GET /api/test-user/tasks/{task_id}")
    try:
        response = requests.get(f"{BASE_URL}/api/test-user/tasks/{task_id}")
        print(f"   Status: {response.status_code}")
        task = response.json()
        print(f"   Task: {task['title']}")
        print(f"   Description: {task['description']}")
    except Exception as e:
        print(f"   ERROR: {e}")

    # Test 6: Update task
    print(f"\n[6]  Testing PUT /api/test-user/tasks/{task_id}")
    update_data = {
        "title": "Complete Phase II hackathon - UPDATED",
        "description": "Build with FastAPI backend and Next.js frontend"
    }
    try:
        response = requests.put(
            f"{BASE_URL}/api/test-user/tasks/{task_id}",
            json=update_data
        )
        print(f"   Status: {response.status_code}")
        task = response.json()
        print(f"   Updated Title: {task['title']}")
    except Exception as e:
        print(f"   ERROR: {e}")

    # Test 7: Toggle completion
    print(f"\n[7]  Testing PATCH /api/test-user/tasks/{task_id}/complete")
    try:
        response = requests.patch(f"{BASE_URL}/api/test-user/tasks/{task_id}/complete")
        print(f"   Status: {response.status_code}")
        task = response.json()
        print(f"   Completed status: {task['completed']}")
    except Exception as e:
        print(f"   ERROR: {e}")

    # Test 8: Filter by status
    print("\n[8]  Testing GET /api/test-user/tasks?status=completed")
    try:
        response = requests.get(f"{BASE_URL}/api/test-user/tasks?status=completed")
        print(f"   Status: {response.status_code}")
        data = response.json()
        print(f"   Completed tasks: {data['total']}")
    except Exception as e:
        print(f"   ERROR: {e}")

    # Test 9: Delete task
    print(f"\n[9]  Testing DELETE /api/test-user/tasks/{task_id}")
    try:
        response = requests.delete(f"{BASE_URL}/api/test-user/tasks/{task_id}")
        print(f"   Status: {response.status_code}")
        print(f"   Task deleted successfully")
    except Exception as e:
        print(f"   ERROR: {e}")

    # Test 10: Verify deletion
    print("\n[10] Verifying deletion - GET /api/test-user/tasks")
    try:
        response = requests.get(f"{BASE_URL}/api/test-user/tasks")
        print(f"   Status: {response.status_code}")
        data = response.json()
        print(f"   Total tasks: {data['total']}")
    except Exception as e:
        print(f"   ERROR: {e}")

    print("\n" + "=" * 60)
    print("SUCCESS All tests completed!\n")
    print("API API Documentation: http://localhost:8000/docs")
    print("DOCS ReDoc: http://localhost:8000/redoc")


if __name__ == "__main__":
    test_endpoints()

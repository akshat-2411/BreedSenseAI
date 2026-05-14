import requests

try:
    response = requests.post("http://localhost:5000/auth/register", data={
        "username": "testuser",
        "email": "test@example.com",
        "password": "password123",
        "confirm_password": "password123"
    })
    print(f"Status Code: {response.status_code}")
    print(response.text[:500])
except Exception as e:
    print(f"Request failed: {e}")

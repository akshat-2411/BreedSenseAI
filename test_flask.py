from app import create_app
import traceback

app = create_app()
app.config['TESTING'] = True
client = app.test_client()

try:
    response = client.post('/auth/register', data={
        "username": "testuser",
        "email": "test@example.com",
        "password": "password123",
        "confirm_password": "password123"
    })
    print(f"Status Code: {response.status_code}")
except Exception as e:
    print("Exception caught!")
    traceback.print_exc()

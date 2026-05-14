import traceback
import io
from PIL import Image
import numpy as np
from app import create_app

app = create_app()
app.config['TESTING'] = True
client = app.test_client()

# Create a dummy user in db
app.db.users.delete_many({"email": "test_predict@example.com"})
app.db.users.insert_one({
    "username": "test_predict",
    "email": "test_predict@example.com",
    "password_hash": "dummy",
    "role": "user"
})

user = app.db.users.find_one({"email": "test_predict@example.com"})

# Create dummy image
img = Image.fromarray(np.uint8(np.random.rand(224, 224, 3) * 255))
img_byte_arr = io.BytesIO()
img.save(img_byte_arr, format='JPEG')
img_byte_arr.seek(0)

print("Starting test...")
with client:
    # login using test_client session
    with client.session_transaction() as sess:
        sess['_user_id'] = str(user['_id'])
        sess['_fresh'] = True
    
    # post to predict multiple times
    for i in range(10):
        try:
            print(f"Request {i+1}...")
            img_byte_arr = io.BytesIO()
            img.save(img_byte_arr, format='JPEG')
            img_byte_arr.seek(0)
            response = client.post('/api/predict', data={
                'image': (img_byte_arr, 'dummy.jpg')
            }, content_type='multipart/form-data')
            print(f"Response: {response.status_code}")
        except Exception as e:
            print("EXCEPTION CAUGHT:")
            traceback.print_exc()
            break

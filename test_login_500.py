import requests
import json

url = "http://localhost:8000/api/v1/auth/login"
data = {
    "email": "raohamzanisar43@gmail.com",
    "password": "String123"
}

print(f"Sending POST request to {url}...")
try:
    response = requests.post(url, json=data)
    print(f"Status Code: {response.status_code}")
    print(f"Response Body: {response.text}")
except Exception as e:
    print(f"Request failed: {e}")

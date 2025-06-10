import requests

print("Testing backend connection...")
try:
    response = requests.get("http://localhost:8000/health", timeout=5)
    print(f"Status: {response.status_code}")
    print(f"Response: {response.text}")
except Exception as e:
    print(f"Error: {e}")
    
print("Test completed.")

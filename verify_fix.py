import sys
print("Python version:", sys.version)
print("Testing imports...")

try:
    import requests
    print("✅ requests imported")
except ImportError as e:
    print("❌ requests failed:", e)

try:
    import time
    print("✅ time imported")
except ImportError as e:
    print("❌ time failed:", e)

try:
    import json
    print("✅ json imported")
except ImportError as e:
    print("❌ json failed:", e)

print("\nTesting syntax by importing the test file...")
try:
    import simple_e2e_test
    print("✅ simple_e2e_test imported successfully")
except Exception as e:
    print("❌ simple_e2e_test failed:", e)

print("\nTesting backend connection...")
try:
    import requests
    response = requests.get("http://localhost:8000/health", timeout=5)
    print(f"✅ Backend responded: {response.status_code}")
    print(f"   Response: {response.json()}")
except Exception as e:
    print(f"❌ Backend connection failed: {e}")

print("\nDone!")

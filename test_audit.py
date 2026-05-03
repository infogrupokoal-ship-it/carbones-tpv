import requests

try:
    response = requests.post("http://127.0.0.1:8000/api/agents/audit-day")
    print(f"Status Code: {response.status_code}")
    with open("response.md", "w", encoding="utf-8") as f:
        f.write(response.text)
    print("Saved response to response.md")
except Exception as e:
    print(f"Connection failed: {e}")

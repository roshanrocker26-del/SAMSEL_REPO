import requests
import sys

def check_api():
    url = "http://127.0.0.1:8000/get-classes/?series=Series 1"
    try:
        response = requests.get(url)
        print(f"Status: {response.status_code}")
        print(f"Content: {response.json()}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    check_api()

import requests
from datetime import datetime

def verify_license_key(key):
    """Check with payment server"""
    try:
        response = requests.post(
            "https://api.resumelyzer.com/verify",
            json={"key": key},
            timeout=5
        )
        return response.json().get("valid", False)
    except:
        return False
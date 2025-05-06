import requests
from flask import request, abort
from werkzeug.exceptions import HTTPException

API_URL = "https://firewall-aghdauayfphmgxhk.southafricanorth-01.azurewebsites.net/predict"
TOKEN = "mon_super_token_secret"

def shield():
    """Flask middleware to check incoming requests using AI model"""
    try:
        # Prepare request data
        data = {
            "method": request.method,
            "url": request.path,
            "headers": dict(request.headers),
            "body": request.get_data(as_text=True)
        }

        print("🔍 Sending data to the AI model...")
        print(f"Request data: {data}")

        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {TOKEN}"
        }

        response = requests.post(API_URL, headers=headers, json=data)
        result = response.json().get("prediction", "").lower()
        print(f"💡 Model response: {result}")

        if "attack" in result:
            print("🚫 Attack detected. Blocking request.")
            abort(403)

    except HTTPException:
        raise  # Re-raise abort(403) and similar errors so Flask handles them

    except Exception as e:
        print(f"[Sufetron] Error: {e}")

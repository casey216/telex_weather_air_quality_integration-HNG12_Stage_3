from fastapi import FastAPI, Request, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List
import requests
from dotenv import load_dotenv
import os

load_dotenv()

app = FastAPI()

# Enable CORS handling
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class Setting(BaseModel):
    label: str
    type: str
    required: bool
    default: str


class MonitorPayload(BaseModel):
    channel_id: str
    return_url: str
    settings: List[Setting]


@app.get("/integration.json")
def get_integration_json(request: Request):
    base_url = str(request.base_url).rstrip("/")

    integration_json = {
        "data": {
            "date": {"created_at": "2025-02-18", "updated_at": "2025-02-18"},
            "descriptions": {
                "app_name": "Weather and Air Quality Monitor",
                "app_description": "A Weather and Air Quality Monitor for a Specific Location",
                "app_logo": "https://ibb.co/SLdFBnf",
                "app_url": base_url,
                "background_color": "#fff",
            },
            "is_active": True,
            "integration_type": "interval",
            "key_features": [
                "- monitors weather conditions",
                "- monitors air quality"
            ],
            "integration_category": "Monitoring & Logging",
            "author": "Kenechi Nzewi",
            "website": base_url,
            "settings": [
                {
                    "label": "location",
                    "type": "text",
                    "required": True,
                    "default": "london"
                },
                {
                    "label": "interval",
                    "type": "text",
                    "required": True,
                    "default": "* * * * *",
                },
            ],
            "target_url": "",
            "tick_url": f"{base_url}/tick"
        }
    }

    return integration_json

def handle_weather_request(payload: MonitorPayload):
    location = payload.settings[0].default

    weather_data = get_weather(location)

    send_message_to_telex(payload, weather_data)

def get_weather(location: str):
    api_key = os.getenv("API_KEY")
    weather_api_url = f"https://api.weatherapi.com/v1/current.json?key={api_key}&q={location}&aqi=yes"

    response = requests.get(weather_api_url)

    return response.json()

@app.post('/tick', status_code=202)
def handle_incoming_request(payload: MonitorPayload, background_tasks: BackgroundTasks):
    background_tasks.add_task(handle_weather_request, payload)
    return {"status": "accepted"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app)

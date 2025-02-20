from tests import client, app
from main import MonitorPayload, Setting
from unittest.mock import patch

def test_get_json():
    response = client.get("/integration.json")
    assert response.status_code == 200
    data = response.json()
    assert "data" in data
    assert data["data"]["descriptions"]["app_name"] == "Weather and Air Quality Monitor"
    assert data["data"]["author"] == "Kenechi Nzewi"


def test_handle_incoming_request(mocker):
    mock_handle_weather_request = mocker.patch("main.handle_weather_request")

    payload = MonitorPayload(
        channel_id="test_channel",
        return_url="http://test/return",
        settings=[Setting(label="location", type="text", required=True, default="london")]
    )

    response = client.post("/tick", json=payload.model_dump())
    assert response.status_code == 202
    assert mock_handle_weather_request.called

    # Verify that the correct arguments were passed to the mock
    mock_handle_weather_request.assert_called_once_with(payload)


def test_weather_request(mocker):
    # Mock the get_weather function to avoid actual API calls
    mock_weather_data = {
        "location": {"name": "London"},
        "current": {
            "temp_c": 15.0,
            "condition": {"text": "Partly Cloudy"},
            "wind_kph": 10,
            "pressure_mb": 1015,
            "air_quality": {
                "co": 0.1,
                "no2": 0.2,
                "o3": 0.3,
                "so2": 0.1,
                "pm2_5": 5,
                "pm10": 10,
                "us-epa-index": 1
            }
        }
    }

    mocker.patch("main.get_weather", return_value=mock_weather_data)
    mock_post = mocker.patch("requests.post", return_value=None)  # Mock requests.post

    payload = MonitorPayload(
        channel_id="test_channel",
        return_url="http://test/return",
        settings=[Setting(label="location", type="text", required=True, default="london")]
    )

    # Send a POST request to the /tick endpoint to trigger the background task
    response = client.post("/tick", json=payload.model_dump())
    assert response.status_code == 202

    # Verify that requests.post was called with the correct data
    expected_message = f"""
    Location: London
    Temp.: 15.0 deg. celsius
    Condition: Partly Cloudy
    Wind Speed: 10 kmph
    Pressure: 1015 milibar
    Air Quality:
        CO2: 0.1
        NO2: 0.2
        O3: 0.3
        SO2: 0.1
        Fine Particle Matter: 5
        Particle Matter: 10
        Air Quality Index: 1
    """
    
    expected_data = {
        "message": expected_message,
        "username": "Weather and Air Quality Monitor",
        "event_name": "Weather and Air Quality check",
        "status": "success"
    }

    mock_post.assert_called_once_with("http://test/return", json=expected_data)


"""
def test_get_weather_details_for_location():
    payload = {
        "channel_id": "0195225b-2d5b-7cda-a837-11c034a0d7bd",
        "return_url": "https://ping.telex.im/v1/return/0195225b-2d5b-7cda-a837-11c034a0d7bd",
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
                "default": "* * * * *"
            }
        ]
    }

    response = client.post("/tick", json=payload)
    assert response.status_code == 202
    data = response.json()
    assert data["status"] == "accepted"
"""
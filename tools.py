#!/usr/bin/env python
# coding: utf-8

import requests
import socket
import ollama

from config import MODEL, SMALL_MODEL, BIG_MODEL

# Configuration constants
# MODEL = "llama3.2:1b"
DUMMY_IP = "46.189.45.146"

TOOL_SCHEMA = [
    {
        "type": "function",
        "function": {
            "name": "get_current_weather",
            "description": "Get the current weather for a city",
            "parameters": {
                "type": "object",
                "properties": {
                    "city": {
                        "type": "string",
                        "description": "The name of the city",
                    },
                },
                "required": ["city"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_city",
            "description": "Get the city for a given IP address",
            "parameters": {
                "type": "object",
                "properties": {
                    "ip_address": {
                        "type": "string",
                        "description": "The IP address to get the city for",
                        "default": "",
                    },
                },
                "required": [],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "make_friendly",
            "description": "Make text more user-friendly and conversational",
            "parameters": {
                "type": "object",
                "properties": {
                    "string": {
                        "type": "string",
                        "description": "Input text to be made more friendly"
                    },
                    "model": {
                        "type": "string",
                        "description": "Language model to use for generation",
                        "default": MODEL
                    }
                },
                "required": []
            }
        }
    }
]

def get_local_ip() -> str:
    """Get the local IP address of the current machine.
    
    Returns:
        str: Local IP address or None if unavailable
    """
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip_address = s.getsockname()[0]
        s.close()
        return ip_address
    except socket.error as e:
        print(f"Error: {e}")
        return None

def get_location_by_ip(ip_address: str) -> dict:
    """Get geographic location information for an IP address using ip-api.com.
    
    Args:
        ip_address (str): IP address to lookup
    
    Returns:
        dict: Location information or None on error
    """
    try:
        response = requests.get(f"http://ip-api.com/json/{ip_address}")
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error: {e}")
        return None

def get_city(ip_address: str = "") -> str:
    """Get city name for an IP address (uses local IP if none provided).
    
    Args:
        ip_address (str): Optional IP address to lookup
    
    Returns:
        str: City name from location data
    """
    if not ip_address:
        ip_address = get_local_ip() or DUMMY_IP
    location = get_location_by_ip(ip_address)
    return location.get("city", "Unknown")

def get_current_weather(city) -> str:
    WEATHER_FORMAT = "Current+weather+for+%l:+%C,+Temperature:+%t,+Feels+like:+%f,+Precipitation+(mm, next+3+hours):+%p,+Wind:+%w"

    """Get current weather data from wttr.in API.
    
    Args:
        city (str): City name to get weather for
    
    Returns:
        str: Formatted weather information string
    """
    print(city)
    city = city["city"].lower()
    url = f'http://wttr.in/{city}?format="{WEATHER_FORMAT}"'
    print(url)
    response = requests.get(url)
    return response.text

def make_friendly(string: str = "", model: str = MODEL) -> dict:
    """Convert technical/textual data into friendly conversational format.
    
    Args:
        string (str): Input text to convert
        model (str): LLM model to use for conversion
    
    Returns:
        dict: Response from the LLM model
    """
    messages = [{
        "role": "user", 
        "content": f"Present this in a friendly, conversational way: {string}. "
    }]
    
    return ollama.chat(
        model=BIG_MODEL,
        messages=messages,
    )

def other(user_input: str = ""):
    """When no other tool is of use, use this one!
    
    Args:
        user_input (str): The user's input
    
    Returns:
        ChatResponse object
    """
    messages = [{
        "role": "user", 
        "content": user_input
    }]
    
    return ollama.chat(
        model=model,
        messages=messages,
    )
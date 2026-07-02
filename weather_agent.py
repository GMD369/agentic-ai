import os
import requests
from dotenv import load_dotenv
import google.generativeai as genai

load_dotenv()

GEMINI_KEY = os.getenv("GEMINI_KEY")
OWM_KEY = os.getenv("OWM_KEY")

genai.configure(api_key=GEMINI_KEY)

model = genai.GenerativeModel("gemini-2.5-flash")

# prompt = "Hey Google, how are you?"

# response = model.generate_content(prompt)

# print(response.text)

def extract_city_from_user_question(user_question: str) -> str:
    prompt = f"""
User said: "{user_question}"

Your job: extract ONLY the city name if user is asking weather.
If not weather related OR city is not mentioned → return NONE.
Return only a city name. No punctuation, no extra text.
"""
    response = model.generate_content(prompt)
    city = response.text.strip()
    return city

def fetch_weather(city: str):
    url = f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={OWM_KEY}&units=metric"
    res = requests.get(url)
    return res.json()

def final_output(user_message: str, weather_json: dict) -> str:

    prompt = f"""
User asked: "{user_message}"
Raw weather data: {weather_json}

Write a natural friendly human answer.
Use temperature in Celsius from the JSON.
Do not show JSON. 3-4 short sentences max.
"""
    
    response = model.generate_content(prompt)
    return response.text


while True:

    user_message = input("User: ")

    if user_message.lower() == "exit":
        break

    city = extract_city_from_user_question(user_message)

    if city == "NONE":
        print("Agent: I could not detect any city in your question.")
        continue
    
    weather_json = fetch_weather(city)

    reply = final_output(user_message, weather_json)

    print("\nAgent: ", reply)
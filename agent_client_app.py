import requests
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
import uvicorn, os

from dotenv import load_dotenv
import google.generativeai as genai

load_dotenv()

GEMINI_KEY = os.getenv("GEMINI_KEY")

# -----------------------------
# GEMINI SETUP
# -----------------------------
genai.configure(api_key=GEMINI_KEY)

def gemini_chat(prompt: str) -> str:
    model = genai.GenerativeModel("gemini-2.0-flash")
    response = model.generate_content(prompt)
    return response.text.strip()

MCP_URL = "http://localhost:8000/jsonrpc"   # MCP Weather Server

app = FastAPI()

# -----------------------------
# HTML UI
# -----------------------------
HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>MCP Weather Agent</title>
    <style>
        body { font-family: Arial; margin: 40px; }
        input { width: 400px; padding: 10px; }
        button { padding: 10px 20px; }
        .result { margin-top: 30px; font-size: 1.2rem; }
    </style>
</head>
<body>
    <h2>MCP Weather Agent (Gemini Powered)</h2>
    <form action="/ask" method="post">
        <input name="query" placeholder="Ask something about weather...">
        <button type="submit">Ask</button>
    </form>
    <div class="result">{{result}}</div>
</body>
</html>
"""

# -----------------------------
# LLM HELPERS
# -----------------------------
def extract_city(user_query: str) -> str:
    prompt = f"""
    Extract ONLY the city name from this weather-related question.
    If multiple cities are present, return the first one.
    User Query: "{user_query}"
    Return only the city name.
    """
    return gemini_chat(prompt)

def convert_to_natural_language(city: str, weather: dict) -> str:
    prompt = f"""
    Convert this structured weather data into a natural language explanation.

    City: {city}
    Weather Data: {weather}

    Keep the answer short, simple, and helpful.
    """
    return gemini_chat(prompt)

# -----------------------------
# MCP CALL
# -----------------------------
def call_mcp_get_weather(city: str):
    payload = {
        "jsonrpc": "2.0",
        "method": "get_weather",
        "params": {"city": city},
        "id": 2
    }

    response = requests.post(MCP_URL, json=payload).json()

    if "error" in response:
        return None, response["error"]["message"]
    
    return response["result"], None

# -----------------------------
# ROUTES
# -----------------------------
@app.get("/", response_class=HTMLResponse)
def home():
    return HTML_TEMPLATE.replace("{{result}}", "")

@app.post("/ask", response_class=HTMLResponse)
async def ask(request: Request):
    form = await request.form()
    query = form.get("query", "")

    city = extract_city(query)
    weather, error = call_mcp_get_weather(city)

    if error:
        result = f"Sorry, I couldn't find weather for '{city}'."
    else:
        result = convert_to_natural_language(city, weather)

    return HTML_TEMPLATE.replace("{{result}}", result)

# -----------------------------
# RUN
# -----------------------------
if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=9000)
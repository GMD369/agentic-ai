from fastapi import FastAPI, Request

app = FastAPI()

# --- Simple in-memory "weather data" (could be a DB or external API) ---
WEATHER_DB = {
    "bengaluru": {"temp_c": 26, "condition": "Partly cloudy", "updated": "2025-11-18T07:00:00Z"},
    "new york": {"temp_c": 8, "condition": "Clear", "updated": "2025-11-18T02:00:00Z"},
}

# --- Helpers for JSON-RPC 2.0 minimal compliance ---
class RPCError(Exception):
    def __init__(self, code, message, data=None):
        self.code = code
        self.message = message

@app.post("/jsonrpc")
async def jsonrpc_endpoint(req: Request):
    payload = await req.json()
    # minimal validation
    method = payload.get("method")
    params = payload.get("params", {})
    request_id = payload.get("id")

    try:
        if method == "discover":
            result = discover()
        elif method == "get_weather":
            result = get_weather(**params)
        else:
            raise RPCError(-32601, f"Method not found: {method}")

        return {"jsonrpc": "2.0", "result": result, "id": request_id}
    except RPCError as e:
        return {"jsonrpc": "2.0", "error": {"code": e.code, "message": e.message}, "id": request_id}

# --- MCP-like discovery: list methods + signatures ---

def discover():
    # In a real MCP server this would follow the protocol's discovery format.
    return {
        "tools": [
            {
                "name": "get_weather",
                "description": "Get current weather for a city (case-insensitive)",
                "params": {"city": "string"},
                "returns": {"temp_c": "number", "condition": "string", "updated": "string"},
            }
        ]
    }

# --- Tool implementation ---

def get_weather(city: str):
    key = city.strip().lower()
    if key in WEATHER_DB:
        return {**WEATHER_DB[key], "city": city}
    else:
        # not found -> return structured error
        raise RPCError(1001, f"Weather for '{city}' not found")

# --- Run: uvicorn mcp_weather_server:app --reload --port 8000 ---

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("mcp_weather_server:app", host="0.0.0.0", port=8000, reload=True)
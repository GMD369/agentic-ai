import requests

URL = "http://localhost:8000/jsonrpc"

# Discover tools
r = requests.post(URL, json={"jsonrpc": "2.0", "method": "discover", "params": {}, "id": 1})
print("DISCOVER ->", r.json())

# Call get_weather
payload = {"jsonrpc": "2.0", "method": "get_weather", "params": {"city": "Bengaluru"}, "id": 2}
r = requests.post(URL, json=payload)
print("CALL ->", r.json())
import requests

API_KEY = "sk-dd5d9c7d7f664092b7ce9230aac48369"  # Replace with your actual API key
API_URL = "https://api.deepseek.com"  # Replace with the correct API URL from DeepSeek docs

headers = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json"
}

data = {
    "query": "Predict the best tractor speed for ploughing a 10-hectare field"
}

response = requests.post(API_URL, json=data, headers=headers)

print(response.json())  # Check if we get a valid response

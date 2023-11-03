import requests
import json

# Skyscanner API endpoint
endpoint = "https://partners.api.skyscanner.net/apiservices/browseroutes/v1.0/US/USD/en-US/SFO-sky/JFK-sky/2022-12"

# Your Skyscanner API key
api_key = "YOUR_API_KEY"

# Set the headers for the API request
headers = {
    "Accept": "application/json",
    "Content-Type": "application/x-www-form-urlencoded",
    "apiKey": api_key,
}

try:
    # Send the API request to get flight information
    response = requests.get(endpoint, headers=headers)
    response.raise_for_status()  # Raise an exception if the API request fails

    # Parse the response JSON
    data = json.loads(response.text)

    # Extract the best ticket information
    best_ticket = data["Quotes"][0]
    price = best_ticket["MinPrice"]
    carrier_id = best_ticket["OutboundLeg"]["CarrierIds"][0]
    carrier_name = next(
        (
            carrier["Name"]
            for carrier in data["Carriers"]
            if carrier["CarrierId"] == carrier_id
        ),
        None,
    )

    # Print the best ticket details
    print(f"Best ticket price: {price} USD")
    print(f"Carrier: {carrier_name}")

except requests.exceptions.HTTPError as err:
    print(f"HTTP Error: {err}")
except json.JSONDecodeError as err:
    print(f"JSON Decode Error: {err}")
except KeyError as err:
    print(f"Key Error: {err}")
except Exception as err:
    print(f"Error: {err}")

# Print the raw response for further investigation
print(response.text)
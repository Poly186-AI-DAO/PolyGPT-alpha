import requests
from bs4 import BeautifulSoup
import urllib.parse

def get_flights(origin, destination, date):
    search_url = "https://matrix.itasoftware.com/flights?"
    search_params = {
        "search": urllib.parse.unquote("eyJ0eXBlIjoib25lLXdheSIsInNsaWNlcyI6W3sib3JpZ2luIjpbIkJLSyJdLCJkZXN0IjpbIk5CTyJdLCJkYXRlcyI6eyJzZWFyY2hEYXRlVHlwZSI6InNwZWNpZmljIiwiZGVwYXJ0dXJlRGF0ZSI6IjIwMjMtMTEtMjAiLCJkZXBhcnR1cmVEYXRlVHlwZSI6ImRlcGFydCIsImRlcGFydHVyZURhdGVNb2RpZmllciI6IjAiLCJkZXBhcnR1cmVEYXRlUHJlZmVycmVkVGltZXMiOltdLCJyZXR1cm5EYXRlVHlwZSI6ImRlcGFydCIsInJldHVybkRhdGVNb2RpZmllciI6IjAiLCJyZXR1cm5EYXRlUHJlZmVycmVkVGltZXMiOltdfX1dLCJvcHRpb25zIjp7ImNhYmluIjoiQ09BQ0giLCJzdG9wcyI6Ii0xIiwiZXh0cmFTdG9wcyI6IjEiLCJhbGxvd0FpcnBvcnRDaGFuZ2VzIjoidHJ1ZSIsInNob3dPbmx5QXZhaWxhYmxlIjoidHJ1ZSJ9LCJwYXgiOnsiYWR1bHRzIjoiMSJ9LCJzb2x1dGlvbiI6eyJzZXNzaW9uSWQiOiJHREswZXAwQ2pYMkY2UGdFM1hwOHJkVkZYIiwidmQiOnRydWUsIm9oIjoiMDZsNFh3VWlPRGFHT09PVWl5S0loU0UiLCJFaSI6bnVsbH19")
    }
    
    response = requests.get(search_url, params=search_params)
    soup = BeautifulSoup(response.text, 'html.parser')

    flights = []

    # Extract flight information from the soup object
    # Modify the code according to the specific HTML structure of the ITA Matrix search results page
    
    return flights

origin = 'Nairobi'
destination = 'Bangkok'
date = '2022-12-01'

flights = get_flights(origin, destination, date)

if len(flights) > 0:
    for flight in flights:
        price = flight['Price']
        carrier = flight['Carrier']
        print(f"Price: {price}, Carrier: {carrier}")
else:
    print("No flights found.")
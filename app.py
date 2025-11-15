import streamlit as st
import pandas as pd
import requests
from geopy.geocoders import Nominatim
from geopy.exc import GeocoderUnavailable
import datetime

# --- This is the new, robust function ---
# Use @st.cache_data to save results.
# add show_spinner=False to not show the "Running..." message for this function
@st.cache_data(show_spinner="Locating addresses...")
def get_coordinates(geolocator, address):
    """
    Safely gets coordinates for an address, with caching and error handling.
    Returns (lat, lon) or (None, None) if not found.
    """
    try:
        location = geolocator.geocode(address)
        if location:
            return location.latitude, location.longitude
        else:
            return None, None
    except GeocoderUnavailable:
        st.error(f"Geocoding service is unavailable. Could not find: {address}")
        return None, None
    except Exception as e:
        st.error(f"An error occurred during geocoding: {e}")
        return None, None

# --- Main App Logic ---

st.markdown("""
# 🚖 Taxi Fare Prediction
### Enter your ride details to estimate the taxi fare.
---
""")

# Ask user for date
d = st.date_input(
    "Schedule your ride:",
    datetime.date(2025, 11, 15))

# Ask user for time
t = st.time_input('Select pickup time:', datetime.time(10, 00))

# Combining pickup date and time
pickup_datetime = datetime.datetime.combine(d, t)

# Initialize the geolocator
geolocator = Nominatim(user_agent="taxifare_prediction_app")

# --- Updated Pickup Location Logic ---
pickup_address = st.text_input('Please type your pickup location', '20 West 34th Street, New York, NY')
pickup_latitude, pickup_longitude = get_coordinates(geolocator, pickup_address)

# STOP the app if the address is not found
if not pickup_latitude or not pickup_longitude:
    st.warning("Could not find pickup address. Please try a different one.")
    st.stop() # Stops the script from running further

st.write('Pickup Latitude and Longitude:', pickup_latitude, pickup_longitude)

# --- Updated Dropoff Location Logic ---
dropoff_address = st.text_input('Please type your destination', '33 E 17th St, New York, NY')
dropoff_latitude, dropoff_longitude = get_coordinates(geolocator, dropoff_address)

# STOP the app if the address is not found
if not dropoff_latitude or not dropoff_longitude:
    st.warning("Could not find destination address. Please try a different one.")
    st.stop() # Stops the script from running further

st.write('Destination Latitude and Longitude:', dropoff_latitude, dropoff_longitude)


# Ask user for total number of passengers
passenger_count = st.selectbox('Choose the number of passengers:', list(range(1, 9)), index=0)
st.write('Total number of passengers:', passenger_count)


# Creating a Map
map_data = pd.DataFrame({
    'lat': [pickup_latitude, dropoff_latitude],
    'lon': [pickup_longitude, dropoff_longitude]
})
st.map(data=map_data, zoom=11)


# Defining model url
url = 'https://taxifare.lewagon.ai/predict'

# Creating a params dictionary for our API
params = {
    'pickup_datetime': pickup_datetime.isoformat(),
    'pickup_longitude': pickup_longitude,
    'pickup_latitude': pickup_latitude,
    'dropoff_longitude': dropoff_longitude,
    'dropoff_latitude': dropoff_latitude,
    'passenger_count': passenger_count
}

# Making an API call
try:
    response = requests.get(url, params=params)
    response.raise_for_status() # Raises an error for bad responses (4xx or 5xx)
    result = response.json()
    fare = result.get('fare')

    # Retrieving prediction result
    st.header("💵 Estimated Fare")
    if fare:
        st.success(f"Estimated Fare: **${fare:.2f}**")
        st.caption("This is an approximation based on historical NYC taxi data.")
    else:
        st.error("The API returned a valid response but no fare. Check prediction logic.")
except requests.exceptions.RequestException as e:
    st.error(f"Failed to call the prediction API: {e}")

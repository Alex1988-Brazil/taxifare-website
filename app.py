import streamlit as st
import pandas as pd
import requests
from geopy.geocoders import Nominatim


st.markdown("""
# 🚖 Taxi Fare Prediction
### Enter your ride details to estimate the taxi fare.
---
""")

# Ask user for date
import datetime

d = st.date_input(
    "Schedule your ride:",
    datetime.date(2025, 11, 15))
st.write('Date of departure:', d)

# Ask user for time
import datetime

t = st.time_input('Select pickup time:', datetime.time(10, 00))

st.write('Time of departure:', t)

# Combining pickup date and time
pickup_datetime = datetime.datetime.combine(d, t)

# Ask user for the PICKUP LOCATION
# Initialize the geolocator
geolocator = Nominatim(user_agent="taxifare_lewagon_project")

# Define the address you want to geocode
pickup_address = st.text_input('Please type your pickup location', '20 West 34th Street, New York, NY')

# Geocode the address
pickup_location = geolocator.geocode(pickup_address)
pickup_latitude = pickup_location.latitude
pickup_longitude = pickup_location.longitude

st.write('Pickup Latitude and Longitude:', pickup_latitude, pickup_longitude)

# Ask user for the DROPOFF LOCATION
# Define the address you want to geocode
dropoff = st.text_input('Please type your destination', '33 E 17th St, New York, NY')

# Geocode the address
dropoff = geolocator.geocode(dropoff)
dropoff_latitude = dropoff.latitude
dropoff_longitude = dropoff.longitude

st.write('Destiantion Latitude and Longitude:', dropoff_latitude, dropoff_longitude)

# Ask user for total number of passengers
def get_select_box_data():

    return pd.DataFrame({
          'number_of_passengers': list(range(1, 5)),
        })

df = get_select_box_data()

passenger_count = st.selectbox('Choose the number of passengers that will join the ride:', df['number_of_passengers'])

st.write('Total number of passengers:', passenger_count)


# Creating a Map
# 1. Create a new DataFrame with one point (Manhattan)
def get_select_box_data():

    return pd.DataFrame({
          'lat': [pickup_latitude, dropoff_latitude],
          'lon': [pickup_longitude, dropoff_longitude]
        })

taxifare_map = get_select_box_data()

# 2. Pass this new DataFrame to st.map
st.map(data=taxifare_map, zoom=11)


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
response = requests.get(url, params=params)
result = response.json()
fare = result.get('fare')

# Retrieving prediction result
st.header("💵 Estimated Fare")
if fare:
    st.success(f"Estimated Fare: **${fare:.2f}**")
    st.caption("This is an approximation based on historical NYC taxi data.")
else:
    st.error("The API did not return a valid fare.")

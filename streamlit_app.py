import streamlit as st
from streamlit_option_menu import option_menu
from datetime import datetime
import pytz
import time
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

st.set_page_config(page_title="Speed and Crowd Monitoring", page_icon="activity")

selected = option_menu(
    menu_title="Dashboard", 
    options=["Home", "Monitoring"],
    icons=["house", "graph-up"], 
    menu_icon="cast",
    default_index=0,
    orientation="horizontal",
)

# Function to get current date and time in GMT+7
def get_current_datetime_gmt7():
    tz = pytz.timezone("Asia/Jakarta")  # GMT+7 timezone
    now = datetime.now(tz)
    date_str = now.strftime("%B %-d")  # Month and day without leading zeros
    day_suffix = get_day_suffix(now.day)  # Add suffix to day
    full_date = f"{date_str}{day_suffix}, {now.year}"  # Full date
    time_str = now.strftime("%H:%M:%S")  # Time
    return f"{full_date}, {time_str}"

# Function to determine the correct suffix for the day
def get_day_suffix(day):
    if 11 <= day <= 13:  # Special case for 11th, 12th, 13th
        return "th"
    else:
        return {1: "st", 2: "nd", 3: "rd"}.get(day % 10, "th")

# Function to fetch data from the Google Sheets CSV link
def fetch_google_sheet_csv(csv_url):
    data = pd.read_csv(csv_url)
    return data

if selected == "Home":
    st.title(f"Capstone Project Group 25")
    st.write("""This website can monitor the crowds that occur at bus stops and the ethics of drivers when passing crowds at bus stops.""")
    st.subheader("Current Date and Time (GMT+7)", divider="gray")
    
    # Create a placeholder for the date and time
    datetime_placeholder = st.empty()
    
    # Update the date and time every second
    while True:
        current_datetime = get_current_datetime_gmt7()
        datetime_placeholder.subheader(f"⏰ {current_datetime}")
        time.sleep(1)  # Update every second

if selected == "Monitoring":
    st.title(f"Speed and Crowd Monitoring")
    st.subheader("🏎️💨 Speed Monitoring", divider="gray")

    # Google Spreadsheet CSV Link
    csv_url = "https://docs.google.com/spreadsheets/d/1KZMz0UJmLzo4R-5uCe61OLcvt0b5LPvrOcABXYSXVFw/export?format=csv"

    try:
        # Fetch data from Google Sheets
        data = fetch_google_sheet_csv(csv_url)

        # Convert 'Timestamp (ESP 1)' to datetime format
        data['Timestamp (ESP 1)'] = pd.to_datetime(data['Timestamp (ESP 1)'])

        # Normalize timestamps to the nearest minute
        data['Normalized Timestamp'] = data['Timestamp (ESP 1)'].dt.floor('T')

        # Filter data for rows where minutes are divisible by 5
        filtered_data = data[data['Normalized Timestamp'].dt.minute % 5 == 0]

        # Plot the speed monitoring graph
        st.subheader("Speed Monitoring Graph")
        plt.figure(figsize=(10, 5))

        # Plot the filtered data
        plt.plot(filtered_data['Normalized Timestamp'], filtered_data['Final Speed'], marker='o', label='Final Speed')

        # Set x-axis ticks to match filtered timestamps
        plt.xticks(filtered_data['Normalized Timestamp'], 
                   filtered_data['Normalized Timestamp'].dt.strftime('%Y-%m-%d %H:%M'), 
                   rotation=45)  # Format as 'YYYY-MM-DD HH:MM' and rotate

        # Add labels, title, and grid
        plt.xlabel("Timestamp (Every 5 Minutes)")
        plt.ylabel("Final Speed")
        plt.title("Final Speed Monitoring Over Time")
        plt.legend()
        plt.grid(True)
        st.pyplot(plt)

    except Exception as e:
        st.error(f"Error fetching or processing data: {e}")

    st.subheader("🚏 Crowd Monitoring", divider="gray")
    st.subheader("📈 Crowd vs Speed Monitoring", divider="gray")
import streamlit as st
from streamlit_option_menu import option_menu
from datetime import datetime
import pytz
import time
import pandas as pd
import matplotlib.pyplot as plt

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
    
    # Speed Monitoring Section
    st.subheader("🏎️💨 Speed Monitoring", divider="gray")
    speed_csv_url = "https://docs.google.com/spreadsheets/d/1KZMz0UJmLzo4R-5uCe61OLcvt0b5LPvrOcABXYSXVFw/export?format=csv"

    try:
        # Fetch and preprocess speed monitoring data
        speed_data = fetch_google_sheet_csv(speed_csv_url)
        speed_data['Timestamp (ESP1)'] = pd.to_datetime(speed_data['Timestamp (ESP1)'])
        speed_data = speed_data.sort_values(by='Timestamp (ESP1)')  # Ensure chronological order
        speed_data['Final Speed'] = pd.to_numeric(speed_data['Final Speed'], errors='coerce')
        speed_data = speed_data.dropna(subset=['Final Speed'])

        # Plot speed monitoring graph
        plt.figure(figsize=(10, 5))
        plt.plot(
            speed_data['Timestamp (ESP1)'],
            speed_data['Final Speed'],
            marker='o',       # Add points
            linestyle='-',     # Connect points with a solid line
            color='blue',      # Blue line
            label='Vehicle Speed'
        )

        # Customize x-axis ticks
        plt.gca().xaxis.set_major_formatter(plt.matplotlib.dates.DateFormatter("%H:%M"))
        plt.xticks(rotation=45)
        plt.xlabel("Timestamp")
        plt.ylabel("Final Speed (Kph)")
        plt.title("Final Speed Monitoring Over Time")
        plt.legend()
        plt.grid(True)
        st.pyplot(plt)

    except Exception as e:
        st.error(f"Error fetching or processing speed data: {e}")

    # Crowd Monitoring Section
    st.subheader("🚏 Crowd Monitoring", divider="gray")
    crowd_csv_url = "https://docs.google.com/spreadsheets/d/10YHVsMEsXq5a23Rjfk8NYfgKhIScL6fCbRKD9HCPYyg/export?format=csv"

    try:
        # Fetch and preprocess crowd monitoring data
        crowd_data = fetch_google_sheet_csv(crowd_csv_url)
        crowd_data['Timestamp'] = pd.to_datetime(crowd_data['Timestamp'])
        crowd_data = crowd_data.sort_values(by='Timestamp')  # Ensure chronological order
        crowd_data['Count'] = pd.to_numeric(crowd_data['Count'], errors='coerce')
        crowd_data = crowd_data.dropna(subset=['Count'])

        # Plot crowd monitoring graph
        plt.figure(figsize=(10, 5))
        plt.plot(
            crowd_data['Timestamp'],
            crowd_data['Count'],
            marker='o',       # Add points
            linestyle='-',     # Connect points with a solid line
            color='green',     # Green line
            label='People Count'
        )

        # Customize x-axis ticks
        plt.gca().xaxis.set_major_formatter(plt.matplotlib.dates.DateFormatter("%H:%M"))
        plt.xticks(rotation=45)
        plt.xlabel("Timestamp")
        plt.ylabel("Number of People")
        plt.title("Crowd Monitoring Over Time")
        plt.legend()
        plt.grid(True)
        st.pyplot(plt)

    except Exception as e:
        st.error(f"Error fetching or processing crowd data: {e}")

    # Crowd vs Speed Monitoring Section
    st.subheader("📈 Crowd vs Speed Monitoring", divider="gray")

    try:
        # Truncate timestamps to only hour and minute
        crowd_data['Truncated Timestamp'] = crowd_data['Timestamp'].dt.floor('T')  # Round down to minute
        speed_data['Truncated Timestamp'] = speed_data['Timestamp (ESP1)'].dt.floor('T')  # Round down to minute

        # Merge the datasets on the truncated timestamps
        merged_data = pd.merge(
            crowd_data,
            speed_data,
            left_on='Truncated Timestamp',
            right_on='Truncated Timestamp',
            how='inner'  # Exact match based on truncated timestamps
        )

        # Check if there are enough data points after merging
        if merged_data.empty:
            st.warning("No matching data found after truncating to hour and minute.")
        else:
            # Plot Crowd vs Speed
            plt.figure(figsize=(10, 5))
            plt.scatter(
                merged_data['Count'],          # x-axis: Crowd Count
                merged_data['Final Speed'],    # y-axis: Final Speed
                color='purple',                # Color of points
                label="Crowd vs Speed"
            )
            plt.xlabel("Crowd Count (Number of People)")
            plt.ylabel("Final Speed (Kph)")
            plt.title("Crowd Count vs Vehicle Speed")
            plt.grid(True)
            plt.legend()
            st.pyplot(plt)

    except Exception as e:
        st.error(f"Error plotting Crowd vs Speed Monitoring: {e}")


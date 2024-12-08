import streamlit as st 
from datetime import datetime
import pytz  
import pandas as pd
import matplotlib.pyplot as plt
import time

st.set_page_config(page_title="Speed and Crowd Monitoring", page_icon="activity")

# Function to get current date and time in GMT+7
def get_current_datetime_gmt7():
    # Set timezone to GMT+7 (Asia/Jakarta)
    timezone = pytz.timezone("Asia/Jakarta")
    now = datetime.now(timezone)
    return now.strftime("%B %d, %Y %H:%M:%S")  # Return formatted date and time

# Function to fetch data from the Google Sheets CSV link
def fetch_google_sheet_csv(csv_url):
    data = pd.read_csv(csv_url)
    return data

# Title and description
st.title(f"Speed and Crowd Monitoring 🖥️")
st.subheader("Capstone project Group 25")
st.write("""This website can monitor the crowds that occur at FTUI bus stops and the ethics of drivers when passing crowds at FTUI bus stops.""")

# Current Date and Time Section
st.subheader("Current Date and Time (GMT+7) ⏰", divider="gray")
datetime_placeholder = st.empty()  # Placeholder to hold current date and time

# Function to display live date and time
def update_datetime():
    while True:
        current_datetime = get_current_datetime_gmt7()  # Get current date and time in GMT+7
        datetime_placeholder.write(f"{current_datetime}")
        time.sleep(1)  # Update every second

# Speed Monitoring Section
st.subheader("Monitoring Results", divider="gray")
st.write("Monitoring data was taken on December 6, 2024 at 08:00 WIB until 18:05 WIB")
st.subheader("🏎️💨 Speed Monitoring", divider="gray")
speed_csv_url = "https://docs.google.com/spreadsheets/d/1KZMz0UJmLzo4R-5uCe61OLcvt0b5LPvrOcABXYSXVFw/export?format=csv"

try:
    # Fetch and preprocess speed monitoring data
    speed_data = fetch_google_sheet_csv(speed_csv_url)
    speed_data['Timestamp (ESP1)'] = pd.to_datetime(speed_data['Timestamp (ESP1)'])
    speed_data = speed_data.sort_values(by='Timestamp (ESP1)')  # Ensure chronological order
    speed_data['Final Speed'] = pd.to_numeric(speed_data['Final Speed'], errors='coerce')
    speed_data = speed_data.dropna(subset=['Final Speed'])

    # Find the highest speed and corresponding timestamp
    max_speed_row = speed_data.loc[speed_data['Final Speed'].idxmax()]
    max_speed = max_speed_row['Final Speed']
    max_speed_time = max_speed_row['Timestamp (ESP1)'].strftime("%H:%M")

    # Plot speed monitoring graph
    plt.figure(figsize=(10, 5))
    plt.plot(
        speed_data['Timestamp (ESP1)'],
        speed_data['Final Speed'],
        marker='o',
        linestyle='-',
        color='blue',
        label='Vehicle Speed'
    )
    plt.gca().xaxis.set_major_formatter(plt.matplotlib.dates.DateFormatter("%H:%M"))
    plt.xticks(rotation=45)
    plt.xlabel("Timestamp")
    plt.ylabel("Final Speed (Kph)")
    plt.title("Final Speed Monitoring Over Time")
    plt.legend()
    plt.grid(True)
    st.pyplot(plt)

    # Display the highest speed
    st.write(f"**The highest speed:** {max_speed} Kph at {max_speed_time}")

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

    # Find the highest crowd count and corresponding timestamp
    max_crowd_row = crowd_data.loc[crowd_data['Count'].idxmax()]
    max_crowd = max_crowd_row['Count']
    max_crowd_time = max_crowd_row['Timestamp'].strftime("%H:%M")

    # Plot crowd monitoring graph
    plt.figure(figsize=(10, 5))
    plt.plot(
        crowd_data['Timestamp'],
        crowd_data['Count'],
        marker='o',
        linestyle='-',
        color='green',
        label='People Count'
    )
    plt.gca().xaxis.set_major_formatter(plt.matplotlib.dates.DateFormatter("%H:%M"))
    plt.xticks(rotation=45)
    plt.yticks(range(0, int(crowd_data['Count'].max()) + 1, 1))  # Set y-axis to integers with step size of 1
    plt.xlabel("Timestamp")
    plt.ylabel("Number of People")
    plt.title("Crowd Monitoring Over Time")
    plt.legend()
    plt.grid(True)
    st.pyplot(plt)

    # Display the highest crowd count
    st.write(f"**The highest crowd count:** {max_crowd} people at {max_crowd_time}")

except Exception as e:
    st.error(f"Error fetching or processing crowd data: {e}")

# Crowd vs Speed Monitoring Section
st.subheader("📈 Crowd vs Speed Monitoring", divider="gray")

try:
    # Truncate timestamps to only hour and minute
    crowd_data['Truncated Timestamp'] = crowd_data['Timestamp'].dt.floor('T')
    speed_data['Truncated Timestamp'] = speed_data['Timestamp (ESP1)'].dt.floor('T')

    # Merge the datasets on the truncated timestamps
    merged_data = pd.merge(
        crowd_data,
        speed_data,
        left_on='Truncated Timestamp',
        right_on='Truncated Timestamp',
        how='inner'
    )

    # Check if there is data after merging
    if merged_data.empty:
        st.warning("No matching data found for Crowd vs Speed Monitoring.")
    else:
        # Calculate mean Final Speed for each Count value
        aggregated_data = merged_data.groupby('Count')['Final Speed'].mean().reset_index()

        # Plot aggregated data
        plt.figure(figsize=(10, 5))
        plt.plot(
            aggregated_data['Count'],
            aggregated_data['Final Speed'],
            marker='o',
            linestyle='-',
            color='purple',
            label='Mean Speed per Crowd Count'
        )
        plt.xlabel("Crowd Count (Number of People)")
        plt.ylabel("Average Speed (Kph)")
        plt.title("Average Speed vs Crowd Count")
        plt.legend()
        plt.grid(True)
        st.pyplot(plt)

except Exception as e:
    st.error(f"Error plotting Crowd vs Speed Monitoring: {e}")

# Call the function to update datetime
update_datetime()
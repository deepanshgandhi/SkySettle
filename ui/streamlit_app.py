import streamlit as st
import requests
from datetime import date

st.title("Airline Compensation Claim Assistant")
st.write("Enter the flight number and flight date to check eligibility for compensation or benefits.")

# Input fields
flight_number = st.text_input("Flight Number (e.g., DL324):")
flight_date = st.date_input("Flight Date:", value=date.today())
date_str = flight_date.strftime("%Y-%m-%d")

# Init session state
if "compensation_fetched" not in st.session_state:
    st.session_state.compensation_fetched = False
if "output_text" not in st.session_state:
    st.session_state.output_text = ""

# Submit button
if st.button("Submit"):
    if not flight_number:
        st.error("Please enter a flight number.")
    else:
        api_url = f"http://localhost:8000/compensation?flight_number={flight_number}&date={date_str}"
        st.info("Sending request to the API...")
        try:
            response = requests.get(api_url, stream=True)
            if response.status_code == 200:
                st.session_state.output_text = ""
                placeholder = st.empty()

                for line in response.iter_lines(decode_unicode=True):
                    if line:
                        st.session_state.output_text += line.strip() + " "

                        formatted_text = (
                            st.session_state.output_text
                            .replace("<think>", "\n## Reasoning\n\n")
                            .replace("</think>", "\n## Final Answer\n\n")
                        )
                        placeholder.markdown("**Response:**\n\n" + formatted_text)
            else:
                st.error(f"API Error {response.status_code}: {response.text}")
        except Exception as e:
            st.error(f"An error occurred: {e}")

# Flight History button (shown only after compensation is fetched)
if st.session_state.compensation_fetched:
    if st.button("Show Flight History for Last 7 Days"):
        stats_url = f"http://localhost:8000/flight-stats?flight_number={flight_number}&date={date_str}"
        st.info("Fetching flight stats...")
        try:
            stats_response = requests.get(stats_url)
            if stats_response.status_code == 200:
                stats = stats_response.json()
                st.markdown("### ✈️ Flight Performance Summary")
                col1, col2, col3 = st.columns(3)
                col1.metric("Total Flights", stats["total_flights"])
                col2.metric("On Time", stats["on_time"])
                col3.metric("Delayed", stats["delayed"])
                st.metric("Cancelled", stats["cancelled"])
                if stats["avg_delay_minutes"]:
                    st.metric("Avg Delay (min)", stats["avg_delay_minutes"])
            else:
                st.error(f"Flight stats error {stats_response.status_code}: {stats_response.text}")
        except Exception as e:
            st.error(f"An error occurred: {e}")

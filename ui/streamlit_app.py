import streamlit as st
import requests
from datetime import date

st.title("Airline Compensation Claim Assistant")
st.write(
    "Enter the flight number and flight date to check eligibility for compensation or benefits."
)

# Input fields
flight_number = st.text_input("Flight Number (e.g., DL324):")
flight_date = st.date_input("Flight Date:", value=date.today())
date_str = flight_date.strftime("%Y-%m-%d")

# Init session state
if "compensation_fetched" not in st.session_state:
    st.session_state.compensation_fetched = False
if "output_text" not in st.session_state:
    st.session_state.output_text = ""
if "flight_details" not in st.session_state:
    st.session_state.flight_details = {}
if "cancellation_reason" not in st.session_state:
    st.session_state.cancellation_reason = ""

if st.session_state.compensation_fetched and st.session_state.output_text:
    st.markdown("### 💬 LLM Answer")
    st.markdown(st.session_state.output_text)

if st.session_state.compensation_fetched and st.session_state.flight_details:
    st.markdown("### ✈️ Flight Details")
    st.json(st.session_state.flight_details)


if st.button("Submit"):
    if not flight_number:
        st.error("Please enter a flight number.")
    else:
        api_url = f"http://localhost:8000/compensation?flight_number={flight_number}&date={date_str}"
        st.info("Sending request to the API...")
        try:
            with requests.get(api_url, stream=True) as response:
                if response.status_code == 200:
                    st.session_state.compensation_fetched = True
                    st.session_state.output_text = ""
                    st.session_state.flight_details = {}

                    placeholder = st.empty()
                    streamed_text = ""

                    for chunk in response.iter_content(
                        chunk_size=1, decode_unicode=True
                    ):
                        streamed_text += chunk
                        placeholder.markdown(
                            "### 💬 LLM Answer\n" + streamed_text + "▌"
                        )

                    st.session_state.output_text = streamed_text.strip()
                else:
                    st.error(f"API Error {response.status_code}: {response.text}")
        except Exception as e:
            st.error(f"An error occurred: {e}")


# Flight History button (shown only after compensation is fetched)
if st.session_state.compensation_fetched:
    if "show_history" not in st.session_state:
        st.session_state.show_history = False

    if st.button("Show Flight History for Last 7 Days"):
        stats_url = f"http://localhost:8000/flight-stats?flight_number={flight_number}&date={date_str}"
        st.info("Fetching flight stats...")
        try:
            stats_response = requests.get(stats_url)
            if stats_response.status_code == 200:
                stats = stats_response.json()
                st.session_state.show_history = True
                st.session_state.flight_stats = stats
            else:
                st.error(
                    f"Flight stats error {stats_response.status_code}: {stats_response.text}"
                )
        except Exception as e:
            st.error(f"An error occurred: {e}")

    if st.session_state.show_history and "flight_stats" in st.session_state:
        stats = st.session_state.flight_stats
        st.markdown("### Flight Performance Summary")
        col1, col2, col3 = st.columns(3)
        col1.metric("Total Flights", stats["total_flights"])
        col2.metric("On Time", stats["on_time"])
        col3.metric("Delayed", stats["delayed"])
        st.metric("Cancelled", stats["cancelled"])
        if stats["avg_delay_minutes"]:
            st.metric("Avg Delay (min)", stats["avg_delay_minutes"])


if st.button("Why was this flight cancelled or delayed?"):
    cancel_url = f"http://localhost:8000/cancellation-reason?flight_number={flight_number}&date={date_str}"
    try:
        with requests.get(cancel_url, stream=True) as cancel_response:
            if cancel_response.status_code == 200:
                streamed_reason = ""
                placeholder = st.empty()

                for chunk in cancel_response.iter_content(
                    chunk_size=1, decode_unicode=True
                ):
                    streamed_reason += chunk
                    placeholder.markdown(
                        "### Cancellation Reason\n" + streamed_reason + "▌"
                    )

                st.session_state.cancellation_reason = streamed_reason.strip()
            else:
                st.session_state.cancellation_reason = (
                    f"Error {cancel_response.status_code}: {cancel_response.text}"
                )

    except Exception as e:
        st.session_state.cancellation_reason = (
            f"Error fetching cancellation reason: {e}"
        )

    if st.session_state.cancellation_reason:
        st.markdown("### Cancellation Reason")
        st.info(st.session_state.cancellation_reason)

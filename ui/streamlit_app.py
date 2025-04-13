import streamlit as st
import requests
from datetime import date

st.title("Airline Compensation Claim Assistant")
st.write("Enter the flight number and flight date to check eligibility for compensation or benefits.")

# Input fields for flight number and flight date
flight_number = st.text_input("Flight Number (e.g., DL324):")
flight_date = st.date_input("Flight Date:", value=date.today())

if st.button("Submit"):
    if not flight_number:
        st.error("Please enter a flight number.")
    else:
        # Format the date as YYYY-MM-DD
        date_str = flight_date.strftime("%Y-%m-%d")
        
        # Your FastAPI endpoint (adjust host/port as needed)
        api_url = f"http://localhost:8000/compensation?flight_number={flight_number}&date={date_str}"

        st.info("Sending request to the API...")
        try:
            # Open a streamed connection to the API
            response = requests.get(api_url, stream=True)
            if response.status_code == 200:
                st.markdown("**Response:**")
                output_container = st.empty()
                output_text = ""
                
                # Process the streamed response line by line
                for line in response.iter_lines(decode_unicode=True):
                    if line:
                        # Accumulate streamed text
                        output_text += line.strip() + " "

                        # Convert <think> tags into headings so users clearly see the reasoning vs. final answer
                        formatted_text = (
                            output_text
                            .replace("<think>", "\n## Reasoning\n\n")
                            .replace("</think>", "\n## Final Answer\n\n")
                        )
                        
                        # Display updated text with markdown headings
                        output_container.markdown(formatted_text)
            else:
                st.error(f"API Error {response.status_code}: {response.text}")
        except Exception as e:
            st.error(f"An error occurred: {e}")

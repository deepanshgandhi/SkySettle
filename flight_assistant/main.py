# flight_assistant/main.py
from fastapi import FastAPI, Query
from fastapi.responses import StreamingResponse, JSONResponse
import requests
import os
import uvicorn
from datetime import datetime, timedelta

from flight_assistant.policy_loader import load_policies
from flight_assistant.lm import call_language_model
from dotenv import load_dotenv
load_dotenv()

app = FastAPI()

RAPIDAPI_KEY = os.getenv("RAPIDAPI_KEY")
RAPIDAPI_HOST = "aerodatabox.p.rapidapi.com"

policies = load_policies("data/airline_policies.json")

def get_flight_details(flight_number: str, date: str):
    url = f"https://aerodatabox.p.rapidapi.com/flights/number/{flight_number}/{date}"
    headers = {
        "x-rapidapi-key": RAPIDAPI_KEY,
        "x-rapidapi-host": RAPIDAPI_HOST
    }
    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        raise Exception(f"Error fetching flight details: {response.status_code} {response.text}")
    
    data = response.json()
    flights = data or []

    if not flights:
        raise Exception("No flight data found.")

    flight = flights[0]

    flight_name = flight.get("airline", {}).get("name", "Unknown")
    source = flight.get("departure", {}).get("airport", {}).get("iata", "Unknown")
    destination = flight.get("arrival", {}).get("airport", {}).get("iata", "Unknown")
    scheduled_time = flight.get("departure", {}).get("scheduledTime", {}).get("local", "Unknown")
    actual_time = flight.get("departure", {}).get("runwayTime", {}).get("local", "Unknown")
    
    return {
        "flight_name": flight_name,
        "source": source,
        "destination": destination,
        "scheduled_time": scheduled_time,
        "actual_time": actual_time
    }

def build_prompt(flight_details, policy):
    prompt = (
        "You are an assistant that determines if a passenger is eligible for benefits based on airline compensation policies. "
        "Review the flight details and the compensation policy below to decide if the passenger qualifies for any benefits (compensation, rebooking, refund, voucher, meals, hotel, etc.). "
        "Be factual, clear, and avoid repeating provided information. "
        "Provide a final answer in 2–4 concise sentences that is direct and to the point, includes the airline name, the relevant details (with dates/times formatted nicely, e.g., 'April 12, 2025 at 6:05 PM local time'), and the eligibility decision. \n\n"
        f"Flight Details:\n"
        f"- Airline: {flight_details['flight_name']}\n"
        f"- From: {flight_details['source']}\n"
        f"- To: {flight_details['destination']}\n"
        f"- Scheduled Departure: {flight_details['scheduled_time']}\n"
        f"- Actual Departure: {flight_details['actual_time']}\n\n"
        f"Compensation Policy:\n{policy}\n\n"
        "Provide the final answer in 2–4 sentences without any extra sections or repeated information. Clearly state if they qualify for anything and DO NOT REPEAT information in the final answer."
    )
    return prompt





@app.get("/compensation")
async def get_compensation(
    flight_number: str = Query(..., description="Flight number (e.g., BA2490)"),
    date: str = Query(..., description="Flight date in YYYY-MM-DD format")
):
    try:
        # Get flight details from AeroDataBox API
        flight_details = get_flight_details(flight_number, date)
        
        # Get compensation policy based on flight name.
        # The key is the flight name returned from the API.
        flight_name = flight_details["flight_name"]
        normalized_name = flight_name.lower()

        # Filter all policies matching that airline (case-insensitive)
        matching_policies = [p for p in policies if p["airline"].lower() == normalized_name]
        if not matching_policies:
            policy = "No compensation policy available for this flight."
        else:
            all_commits = []
            all_does_not_commit = []
            for p in matching_policies:
                all_commits.extend(p.get("commits", []))
                all_does_not_commit.extend(p.get("does_not_commit", []))
            
            policy = (
                f"Commits:\n- " + "\n- ".join(all_commits) +
                f"\n\nDoes Not Commit:\n- " + "\n- ".join(all_does_not_commit)
            )
        
        # Build prompt for the language model
        prompt = build_prompt(flight_details, policy)
        
        # Call the language model and stream the response word by word
        stream_generator = call_language_model(prompt)
        return StreamingResponse(stream_generator, media_type="text/plain")
    
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})


@app.get("/flight-stats")
async def get_flight_stats(
    flight_number: str = Query(..., description="Flight number (e.g., DL324)"),
    date: str = Query(..., description="Flight date in YYYY-MM-DD format")
):
    try:
        end_date = datetime.strptime(date, "%Y-%m-%d")
        start_date = end_date - timedelta(days=6)
        url = (
            f"https://aerodatabox.p.rapidapi.com/flights/number/{flight_number}/"
            f"{start_date.date()}/{end_date.date()}?dateLocalRole=Both"
        )

        headers = {
            "x-rapidapi-key": RAPIDAPI_KEY,
            "x-rapidapi-host": RAPIDAPI_HOST
        }

        response = requests.get(url, headers=headers)
        if response.status_code != 200:
            raise Exception(f"Failed to fetch historical data: {response.status_code}")

        flights = response.json() or []

        stats = {
            "total_flights": 0,
            "on_time": 0,
            "delayed": 0,
            "cancelled": 0,
            "avg_delay_minutes": 0.0,
            "details": []
        }

        total_delay = 0
        for flight in flights:
            stats["total_flights"] += 1
            status = flight.get("status", "").lower()
            flight_date = flight.get("departure", {}).get("scheduledTime", {}).get("local", "Unknown")

            if status == "cancelled":
                stats["cancelled"] += 1
                stats["details"].append({
                    "date": flight_date,
                    "status": "Cancelled",
                    "delay_minutes": None
                })
                continue

            sched = flight.get("departure", {}).get("scheduledTime", {}).get("utc")
            actual = flight.get("departure", {}).get("runwayTime", {}).get("utc")
            if sched and actual:
                sched_time = datetime.strptime(sched, "%Y-%m-%d %H:%MZ")
                actual_time = datetime.strptime(actual, "%Y-%m-%d %H:%MZ")
                delay_min = (actual_time - sched_time).total_seconds() / 60

                if delay_min > 15:
                    stats["delayed"] += 1
                else:
                    stats["on_time"] += 1

                total_delay += delay_min
                stats["details"].append({
                    "date": flight_date,
                    "status": "Delayed" if delay_min > 15 else "On Time",
                    "delay_minutes": round(delay_min)
                })
            else:
                stats["details"].append({
                    "date": flight_date,
                    "status": "Unknown (missing times)",
                    "delay_minutes": None
                })

        if stats["delayed"] > 0:
            stats["avg_delay_minutes"] = round(total_delay / stats["delayed"], 2)

        return JSONResponse(content=stats)

    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)

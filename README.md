# SkySettle

AI-powered tool that checks flight compensation eligibility and auto-files claims for delayed or canceled flights.

## 📋 Overview

SkySettle uses airline policy data and flight information to help travelers understand their compensation rights when flights are delayed or canceled. The app provides:

- Eligibility checking for compensation or benefits
- Flight status monitoring
- Historical flight statistics
- Cancellation/delay reason analysis
- Airline policy information

## 🔧 Setup Instructions

```bash
# Create a virtual environment
python3 -m venv venv

# Activate the virtual environment
# On macOS/Linux:
source venv/bin/activate

# On Windows:
venv\Scripts\activate

# Install required packages
pip install -r requirements.txt
```

## 🛠️ Environment Variables

Create a `.env` file in the root directory with the following content:

```bash
GROQ_API_KEY=your_groq_api_key_here
RAPIDAPI_KEY=your_rapidapi_key_here
BRAVE_API_KEY=your_brave_api_key_here
```

These are required to access:
- Language model (via Groq) for generating compensation eligibility explanations
- Flight information (via AeroDataBox/RapidAPI) for real-time and historical flight data
- Web search (via Brave Search API) for gathering relevant contextual information

## 🚀 Running the App

### Start the Backend (FastAPI)

```bash
uvicorn flight_assistant.main:app --reload
```

This will run the FastAPI server locally at http://127.0.0.1:8000.

### Start the UI (Streamlit)

```bash
streamlit run ui/streamlit_app.py
```

This will launch the Streamlit interface in your browser at http://localhost:8501.

## 📊 Features

### Flight Compensation Eligibility

Enter your flight number and date to check what compensation or benefits you may be entitled to receive. The tool matches your flight details with airline policies for:
- Rebooking options
- Meal vouchers
- Hotel accommodations
- Transportation
- Credit/travel vouchers
- Cash compensation
- Frequent flyer miles

### Flight Status History

View a summary of the flight's performance over the past 7 days:
- Total flights
- On-time percentage
- Delay frequency
- Cancellation rates
- Average delay times

### Cancellation/Delay Reason Analysis

Get AI-generated explanations for why your flight was canceled or delayed based on:
- Flight details
- Web search results
- Historical flight patterns

## 🧰 Project Structure

- `data/airline_policies.json`: Contains structured airline policy data for major carriers
- `flight_assistant/`: Core backend logic
  - `main.py`: FastAPI server implementation with endpoints
  - `lm.py`: Language model integration (Groq API)
  - `policy_loader.py`: Loads and parses airline policies
- `scraper/`: Tools for gathering policy information
  - `scraper.py`: Web scraper for airline policy data from transportation.gov
- `ui/`: Frontend interface
  - `streamlit_app.py`: Streamlit user interface for the application

## 💻 API Endpoints

- `/compensation`: Get compensation eligibility details
  - Parameters: `flight_number`, `date`
  - Returns: Text stream with eligibility assessment

- `/flight-stats`: Retrieve historical flight statistics
  - Parameters: `flight_number`, `date`
  - Returns: JSON with flight performance metrics

- `/cancellation-reason`: Get AI-generated explanation for flight disruption
  - Parameters: `flight_number`, `date`
  - Returns: Text stream with likely reason for delay/cancellation

## 🔄 Data Sources

- **Airline Policies**: Scraped from the Department of Transportation's Airline Customer Service Dashboard
- **Flight Data**: Retrieved from AeroDataBox API via RapidAPI
- **Contextual Information**: Obtained through Brave Search API

## 🔧 Updating Airline Policies

To update the airline policy database with the latest information, run:

```bash
python -m scraper.scraper
```

This will scrape the latest policy information and save it to `data/airline_policies.json`.

## 📝 Dependencies

- FastAPI: Backend web framework
- Streamlit: User interface framework
- Groq API: Language model for generating responses
- AeroDataBox/RapidAPI: Flight data and statistics
- Brave Search API: Web search for contextual information
- BeautifulSoup4: Web scraping airline policies
- Python-dotenv: Environment variable management

## 🔒 Security Notes

- This application requires API keys that should be kept secure
- Do not commit your `.env` file to version control
- Consider using a secrets manager for production deployments

## 📋 License

This project is intended for educational and personal use.

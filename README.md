# SkySettle
AI-powered tool that checks flight compensation eligibility and auto-files claims for delayed or canceled flights.

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
Create a .env file in the root directory with the following content:
```bash
GROQ_API_KEY=your_groq_api_key_here
RAPIDAPI_KEY=your_rapidapi_key_here
```
These are required to access the language model (via Groq) and flight information (via AeroDataBox/RapidAPI).

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
This will launch the Streamlit interface in your browser.

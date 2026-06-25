# Support Ticket Classification API

A FastAPI-based web service that automatically categorizes incoming customer support tickets using Google's Gemini LLM. It analyzes free-text customer complaints and instantly determines the problem type, severity, appropriate department, and summarizes the issue for a human agent.

## Features

- **Automated Triage**: Classifies tickets into predefined categories (e.g., `wrong_transfer`, `phishing_or_social_engineering`).
- **Severity & Routing**: Assesses the urgency of the ticket and routes it to the correct department.
- **Safety First**: Implements strict safety guardrails to ensure customer summaries never ask for sensitive info like PINs, OTPs, or passwords.
- **Robust Fallback Engine**: Includes a heuristic, rule-based fallback system that takes over seamlessly if the LLM API is unavailable, unconfigured, or rate-limited.
- **Type-Safe Validation**: Built with Pydantic and Enums to guarantee that API responses precisely match the required JSON schema.

## Project Structure

```text
support-ticket/
├── app/
│   ├── main.py                # FastAPI app entry point
│   ├── routes/                # API Endpoints
│   │   ├── health.py          # GET /health
│   │   └── tickets.py         # POST /sort-ticket
│   ├── schemas/               # Pydantic validation models
│   │   └── ticket.py
│   └── services/              # Core business logic
│       └── classifier.py      # LLM connection & fallback heuristics
├── .env.example               # Template for environment variables
├── requirements.txt           # Project dependencies
└── test_main.py               # Pytest suite
```

## Setup & Installation

1. **Clone the repository:**
   Ensure you are in the project root folder (`support-ticket`).

2. **Create and activate a virtual environment:**
   ```bash
   # Windows
   python -m venv venv
   .\venv\Scripts\activate

   # macOS/Linux
   python3 -m venv venv
   source venv/bin/activate
   ```

3. **Install Dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Environment Variables:**
   Copy the example environment file and add your Gemini API Key.
   ```bash
   cp .env.example .env
   ```
   *Edit `.env` and replace `your_gemini_api_key_here` with your actual Google Gemini API key.*

## Running the API

Start the FastAPI development server using `uvicorn`:

```bash
uvicorn app.main:app --reload
```
*Note: The API will run on `http://127.0.0.1:8000` by default.*

## Endpoints

### 1. `GET /health`
Returns a simple JSON payload confirming the service is online.
**Response:** `{"status": "ok"}`

### 2. `POST /sort-ticket`
Analyzes a support ticket and returns its classification.
**Request Body:**
```json
{
  "ticket_id": "T-001",
  "message": "Someone called asking my OTP, is that bKash?"
}
```
**Response:**
```json
{
  "ticket_id": "T-001",
  "case_type": "phishing_or_social_engineering",
  "severity": "critical",
  "department": "fraud_risk",
  "agent_summary": "Customer reported receiving a call requesting their OTP.",
  "human_review_required": true,
  "confidence": 0.95
}
```

## Running Tests

The application includes a robust test suite covering the core requirements. Run the test suite via `pytest`:

```bash
pytest -v
```

The tests will automatically test against the sample cases to verify both the routing paths and the classification behavior.

## Deployment

This service is production-ready. It can be easily deployed to platforms like Render, Railway, Fly.io, or Vercel using standard Python ASGI deployment practices. Just ensure the `GEMINI_API_KEY` is added to your deployment platform's environment variables.

### Docker
A `Dockerfile` is included for easy containerization.
To build the image:
```bash
docker build -t support-ticket-api .
```

To run the container:
```bash
docker run -p 8000:8000 -e GEMINI_API_KEY=your_actual_key_here support-ticket-api
```

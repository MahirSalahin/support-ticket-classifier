from fastapi import FastAPI
from dotenv import load_dotenv
import uvicorn

# Load environment variables
load_dotenv()

from app.routes import health, tickets

app = FastAPI(
    title="Support Ticket API",
    description="API for classifying customer support tickets",
    version="1.0.0"
)

# Include routers
app.include_router(health.router)
app.include_router(tickets.router)

if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)

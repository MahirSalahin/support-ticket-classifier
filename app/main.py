from fastapi import FastAPI
from dotenv import load_dotenv
import uvicorn

# Load environment variables
load_dotenv()

from app.routes import health, tickets
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware
from app.core.limiter import limiter

app = FastAPI(
    title="Support Ticket Classifier API",
    description="API for classifying customer support tickets",
    version="1.0.0"
)

# Setup rate limiting
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
app.add_middleware(SlowAPIMiddleware)

# Include routers
app.include_router(health.router)
app.include_router(tickets.router)

if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)

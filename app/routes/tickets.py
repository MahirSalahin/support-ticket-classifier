from fastapi import APIRouter, Request
from app.schemas.ticket import TicketRequest, TicketResponse
from app.services.classifier import classify_ticket
from app.core.limiter import limiter

router = APIRouter()

@router.post("/sort-ticket", response_model=TicketResponse, tags=["Tickets"])
@limiter.limit("10/minute")
async def sort_ticket(request: Request, payload: TicketRequest):
    return await classify_ticket(payload)

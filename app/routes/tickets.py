from fastapi import APIRouter
from app.schemas.ticket import TicketRequest, TicketResponse
from app.services.classifier import classify_ticket

router = APIRouter()

@router.post("/sort-ticket", response_model=TicketResponse, tags=["Tickets"])
async def sort_ticket(request: TicketRequest):
    return await classify_ticket(request)

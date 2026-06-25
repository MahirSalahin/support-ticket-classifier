import os
import json
import google.generativeai as genai
from app.schemas.ticket import TicketRequest, TicketResponse, CaseType, Severity, Department

API_KEY = os.environ.get("GEMINI_API_KEY")
if API_KEY:
    genai.configure(api_key=API_KEY)
    
def get_classification_model():
    return genai.GenerativeModel("gemini-1.5-flash", system_instruction="""
    You are an expert customer support ticket classifier for a digital finance company.
    Your job is to read a customer message and return a JSON classification with the following rules:

    1. case_type:
       - 'wrong_transfer': Money sent to the wrong recipient
       - 'payment_failed': Transaction failed but balance may be deducted
       - 'refund_request': Customer is asking for a refund
       - 'phishing_or_social_engineering': Suspicious calls, SMS, or someone asking for PIN, OTP, or password
       - 'other': Anything not covered above

    2. department:
       - 'customer_support': other, low severity refund_request
       - 'dispute_resolution': wrong_transfer, contested refund_request
       - 'payments_ops': payment_failed
       - 'fraud_risk': phishing_or_social_engineering

    3. severity: 'low', 'medium', 'high', or 'critical'. Phishing is usually critical. Payment issues are usually high.

    4. human_review_required: Must be true for critical severity or phishing_or_social_engineering cases.

    5. agent_summary: A one or two sentence neutral summary describing the ticket.
       SAFETY RULE (CRITICAL): The agent_summary MUST NEVER ask the customer to share PIN, OTP, password, or full card number. Do not even suggest it.

    6. confidence: A float between 0.0 and 1.0 representing your confidence in this classification.
    """)

async def classify_ticket(request: TicketRequest) -> TicketResponse:
    if not API_KEY:
        return fallback_classifier(request)
        
    model = get_classification_model()
    
    prompt = f"Ticket ID: {request.ticket_id}\nChannel: {request.channel}\nLocale: {request.locale}\nMessage: {request.message}"
    
    try:
        response = model.generate_content(
            prompt,
            generation_config=genai.GenerationConfig(
                response_mime_type="application/json",
                response_schema=TicketResponse,
                temperature=0.1
            )
        )
        result_dict = json.loads(response.text)
        
        summary_lower = result_dict.get("agent_summary", "").lower()
        if any(word in summary_lower for word in ["pin", "otp", "password", "card number"]):
            result_dict["agent_summary"] = "Customer reported an issue. (Original summary suppressed due to safety rules regarding sensitive info)."
            
        return TicketResponse(**result_dict)
    except Exception as e:
        print(f"Error calling Gemini API: {e}")
        return fallback_classifier(request)

def fallback_classifier(request: TicketRequest) -> TicketResponse:
    """A very basic rule-based classifier if LLM fails or API key is missing."""
    msg = request.message.lower()
    
    case_type = CaseType.other
    severity = Severity.low
    department = Department.customer_support
    human_review = False
    
    if "wrong" in msg and ("number" in msg or "transfer" in msg):
        case_type = CaseType.wrong_transfer
        severity = Severity.high
        department = Department.dispute_resolution
    elif "fail" in msg or "deduct" in msg:
        case_type = CaseType.payment_failed
        severity = Severity.high
        department = Department.payments_ops
    elif "refund" in msg:
        case_type = CaseType.refund_request
        severity = Severity.low
        department = Department.customer_support
    elif "otp" in msg or "pin" in msg or "password" in msg or "scam" in msg or "phishing" in msg:
        case_type = CaseType.phishing_or_social_engineering
        severity = Severity.critical
        department = Department.fraud_risk
        human_review = True
        
    if severity == Severity.critical or case_type == CaseType.phishing_or_social_engineering:
        human_review = True
        
    return TicketResponse(
        ticket_id=request.ticket_id,
        case_type=case_type,
        severity=severity,
        department=department,
        agent_summary="Customer reported an issue.", 
        human_review_required=human_review,
        confidence=0.5 
    )

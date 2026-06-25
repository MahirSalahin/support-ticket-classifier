import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}

test_cases = [
    (
        "T-001",
        "I sent 3000 to wrong number",
        "wrong_transfer",
        "high"
    ),
    (
        "T-002",
        "Payment failed but balance deducted",
        "payment_failed",
        "high"
    ),
    (
        "T-003",
        "Someone called asking my OTP, is that bKash?",
        "phishing_or_social_engineering",
        "critical"
    ),
    (
        "T-004",
        "Please refund my last transaction, I changed my mind",
        "refund_request",
        "low"
    ),
    (
        "T-005",
        "App crashed when I opened it",
        "other",
        ["low", "medium"]
    )
]

@pytest.mark.parametrize("ticket_id, message, expected_case, expected_severity", test_cases)
def test_sort_ticket(ticket_id, message, expected_case, expected_severity):
    payload = {
        "ticket_id": ticket_id,
        "message": message
    }
    
    response = client.post("/sort-ticket", json=payload)
    assert response.status_code == 200
    
    data = response.json()
    assert data["ticket_id"] == ticket_id
    assert data["case_type"] == expected_case
    
    if isinstance(expected_severity, list):
        assert data["severity"] in expected_severity
    else:
        assert data["severity"] == expected_severity
        
    if data["severity"] == "critical":
        assert data["human_review_required"] is True

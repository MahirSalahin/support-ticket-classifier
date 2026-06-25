from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def run_tests():
    print("Testing /health")
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
    print("Health check passed.\n")

    print("Testing /sort-ticket (Fallback Mode)")
    test_cases = [
        {
            "payload": {
                "ticket_id": "T-001",
                "message": "I sent 3000 to wrong number"
            },
            "expected_case": "wrong_transfer",
            "expected_severity": "high"
        },
        {
            "payload": {
                "ticket_id": "T-002",
                "message": "Payment failed but balance deducted"
            },
            "expected_case": "payment_failed",
            "expected_severity": "high"
        },
        {
            "payload": {
                "ticket_id": "T-003",
                "message": "Someone called asking my OTP, is that bKash?"
            },
            "expected_case": "phishing_or_social_engineering",
            "expected_severity": "critical"
        },
        {
            "payload": {
                "ticket_id": "T-004",
                "message": "Please refund my last transaction, I changed my mind"
            },
            "expected_case": "refund_request",
            "expected_severity": "low"
        },
        {
            "payload": {
                "ticket_id": "T-005",
                "message": "App crashed when I opened it"
            },
            "expected_case": "other",
            "expected_severity": ["low", "medium"]
        }
    ]

    for i, tc in enumerate(test_cases, 1):
        payload = tc["payload"]
        print(f"Test case {i}: {payload['message']}")
        response = client.post("/sort-ticket", json=payload)
        assert response.status_code == 200
        data = response.json()
        print(f"  Received: {data['case_type']} | {data['severity']}")
        if isinstance(tc["expected_severity"], list):
            assert data["severity"] in tc["expected_severity"], f"Expected one of {tc['expected_severity']}, got {data['severity']}"
        else:
            assert data["severity"] == tc["expected_severity"], f"Expected {tc['expected_severity']}, got {data['severity']}"
            
        if data["severity"] == "critical":
            assert data["human_review_required"] is True
            
    print("\nAll tests passed successfully!")

if __name__ == "__main__":
    run_tests()

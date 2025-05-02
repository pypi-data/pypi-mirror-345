"""
Example payment service with GDPR compliance issues.
"""
import requests
import json

class PaymentService:
    def __init__(self, api_key: str, endpoint: str = "https://api.thirdparty.com"):
        self.api_key = api_key
        self.endpoint = endpoint
        
    def process_payment(self, user_data: dict, amount: float):
        """
        Process a payment using third-party API.
        
        Args:
            user_data: User personal information
            amount: Payment amount
        """
        payload = {
            "api_key": self.api_key,
            "amount": amount,
            "user": {
                "name": user_data.get("name"),
                "email": user_data.get("email"),
                "address": user_data.get("address"),
                "credit_card": user_data.get("credit_card"),
                "cvv": user_data.get("cvv")
            }
        }
        
        # GDPR Issue: No consent check before processing sensitive data
        # GDPR Issue: Sending data to third-party without verification
        response = requests.post(self.endpoint, data=json.dumps(payload))
        
        if response.status_code == 200:
            return {"success": True, "transaction_id": response.json().get("transaction_id")}
        else:
            return {"success": False, "error": response.json().get("error")}
    
    def store_payment_info(self, user_id: str, payment_info: dict):
        """
        Store payment information for future use.
        
        Args:
            user_id: User identifier
            payment_info: Payment information
        """
        # GDPR Issue: Storing sensitive data without proper safeguards
        with open(f"payments/{user_id}.json", "w") as f:
            json.dump(payment_info, f)
        
        return True
    
    # GDPR Issue: Missing data deletion functionality
        
def main():
    service = PaymentService(api_key="test_api_key")
    
    user_data = {
        "name": "John Doe",
        "email": "john@example.com",
        "address": "123 Main St, New York, US",
        "credit_card": "4111111111111111",
        "cvv": "123"
    }
    
    result = service.process_payment(user_data, 99.99)
    print(result)
    
if __name__ == "__main__":
    main() 
from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional

class Transaction(BaseModel):
    transaction_id: str
    amount: float = Field(gt=0, description="Transaktionsbelopp måste vara positivt")
    timestamp: datetime
    currency: str
    sender_account: str
    receiver_account: str
    sender_country: str
    sender_municipality: str
    receiver_country: str
    receiver_municipality: str
    transaction_type: str
    notes: Optional[str]  # Kan vara tomt


#%%
data = {
    "transaction_id": "12345",
    "amount": 100,
    "timestamp": "2025-05-22T08:44:00",
    "currency": "EUR",
    "sender_account": "ABC123",
    "receiver_account": "XYZ789",
    "sender_country": "Sweden",
    "sender_municipality": "Stockholm",
    "receiver_country": "Germany",
    "receiver_municipality": "Berlin",
    "transaction_type": "purchase",
    "notes": None
}


try:
    transaction = Transaction(**data)
    print(transaction)
except Exception as e:
    print(f"Fel vid validering: {e}")

#%%
valid_transactions = []
invalid_transactions = []

for index, row in df.iterrows():
    try:
        transaction = Transaction(**row.to_dict())
        valid_transactions.append(transaction)
    except Exception as e:
        invalid_transactions.append((index, str(e)))

print(f"Antal giltiga transaktioner: {len(valid_transactions)}")
print(f"Antal ogiltiga transaktioner: {len(invalid_transactions)}")

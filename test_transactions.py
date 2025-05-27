# Här testar vi dataformat och validering

import pytest
from unittest.mock import MagicMock
from datetime import datetime
from main import clean_amount, clean_timestamp, normalize_currency
from models import Transaction


@pytest.fixture
def mock_db():

    db = MagicMock()


    db.insert_transaction.return_value = True

    return db



def test_clean_amount():
    assert clean_amount("1 234,56") == 1234.56
    assert clean_amount("  500.00 ") == 500.0
    assert clean_amount("") is None
    assert clean_amount("abcd") is None
    assert clean_amount("-500,00") == -500.0  # Testar negativt värde

def test_clean_timestamp():
    assert clean_timestamp("2023-05-26 12:30:45") == "2023-05-26 12:30:45"
    assert clean_timestamp("20230526 12:30:45") == "2023-05-26 12:30:45"
    assert clean_timestamp("invalid_timestamp") is None

def test_normalize_currency():
    assert normalize_currency("USD") == "USD"
    assert normalize_currency("rmb") == "CNY"
    assert normalize_currency(" ") is None
    assert normalize_currency("eur") == "EUR"  # Testar annan valuta



# Här testar vi databasinmatningen på sätt 1



def test_insert_transaction(mock_db):
    new_transaction = Transaction(
        transaction_id='T123',
        timestamp=datetime.strptime("2023-05-26 12:30:45", "%Y-%m-%d %H:%M:%S"),
        amount=1000.50,
        currency="USD",
        sender_account="A001",
        receiver_account="A002",
        sender_country="SE",
        sender_municipality="Stockholm",
        receiver_country="US",
        receiver_municipality="New York",
        transaction_type="Payment",
        notes="Test transaction"
    )

    mock_db.add(new_transaction)
    mock_db.commit()

    retrieved = mock_db.query(Transaction).filter_by(transaction_id="T123").first()
    assert retrieved is not None, "Transaktionen kunde inte hittas"
    assert retrieved.amount == 1000.50, "Beloppet matchar inte"




   # sätt 2 att ansluta till databas



    import pytest
    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker
    from db import Base, Transaction
    from datetime import datetime

    @pytest.fixture
    def test_session():
        engine = create_engine("sqlite:///:memory:", echo=False)
        Base.metadata.create_all(engine)
        Session = sessionmaker(bind=engine)
        return Session()

    def test_insert_transaction(test_session):
        new_transaction = Transaction(
            transaction_id='T123',
            timestamp=datetime.strptime("2023-05-26 12:30:45", "%Y-%m-%d %H:%M:%S"),
            amount=1000.50,
            currency="USD",
            sender_account="A001",
            receiver_account="A002",
            sender_country="SE",
            sender_municipality="Stockholm",
            receiver_country="US",
            receiver_municipality="New York",
            transaction_type="Payment",
            notes="Test transaction"
        )

        test_session.add(new_transaction)
        test_session.commit()

        retrieved = test_session.query(Transaction).filter_by(transaction_id="T123").first()
        assert retrieved is not None
        assert retrieved.amount == 1000.50


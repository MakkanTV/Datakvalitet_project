import logging
from models import Transaction
from datetime import datetime

def process_transaction(session, amount, customer_id, bank_id):
    logging.info(f"Start transaction - customer:{customer_id}, bank: {bank_id}, amount: {amount}")
    try:
        transaction = Transaction(
            amount=amount,
            time=datetime.now(),
            customer_id=customer_id,
            bank_id=bank_id
        )
        session.add(transaction)
        session.commit()
        logging.info(f"Transaction completed with id: {transaction.id}")
    except Exception as e:
        session.rollback()
        logging.error(f"Fel vid transaktion för kund Error transaction for customer: {customer_id}: {e}")
        raise


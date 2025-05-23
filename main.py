import logging
import psycopg2
from db import init_db,session
from transactions_handler import process_transaction

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

def main():
    logging.info("Program started")

    try:
        process_transaction(session, amount=100.0, customer_id=1, bank_id=1)
    except Exception as e:
        logging.error(f"Transaction failed: {e}")

    logging.info("Program ended")

if __name__ == "__main__":
    main()
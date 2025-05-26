import logging
import psycopg2
import csv
from datetime import datetime
from db import init_db, session
from transactions_handler import process_transaction

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

required_fields = [
    "transaction_id", "timestamp", "amount", "currency",
    "sender_account", "receiver_account",
    "sender_country", "sender_municipality",
    "receiver_country", "receiver_municipality",
    "transaction_type"
]

def clean_amount(value):
    if not value:
        return None
    value = value.replace(" ", "").replace(",", ".")
    try:
        return float(value)
    except ValueError:
        return None

def clean_timestamp(ts):
    formats = ["%Y-%m-%d %H:%M:%S", "%Y%m%d %H:%M:%S"]
    for fmt in formats:
        try:
            parsed = datetime.strptime(ts.strip(), fmt)
            return parsed.strftime("%Y-%m-%d %H:%M:%S")
        except ValueError:
            continue
    return None

def normalize_currency(currency):
    if not currency:
        return None
    code = currency.strip().upper()
    return "CNY" if code == "RMB" else code

def main():
    logging.info("Program started")
    init_db()

    conn = psycopg2.connect("dbname=datakvalitet user=postgres password=password1234 host=localhost port=5432")
    cur = conn.cursor()

    try:
        with open("transactions.csv", newline="", encoding="utf-8") as f, \
             open("rejected_transactions.csv", "a", newline="", encoding="utf-8") as rejected_files:

            reader = csv.DictReader(f)
            field_names = required_fields + ["notes"]
            rejected_writer = csv.DictWriter(rejected_files, fieldnames=field_names)

            if rejected_files.tell() == 0:
                rejected_writer.writeheader()

            cur.execute("BEGIN;")

            for row in reader:
                try:
                    for field in required_fields:
                        if not row.get(field) or row[field].strip() == "":
                            raise ValueError(f"{field} saknar värde")

                    timestamp = clean_timestamp(row["timestamp"])
                    if not timestamp:
                        raise ValueError(f"Ogiltigt timestamp format: {row['timestamp']}")

                    amount = clean_amount(row["amount"])
                    if amount is None:
                        raise ValueError(f"Ogiltigt belopp: {row['amount']}")

                    currency = normalize_currency(row["currency"])
                    if not currency:
                        raise ValueError(f"Saknar eller ogiltig valuta: {row['currency']}")

                    cur.execute("""
                        INSERT INTO transactions (
                            transaction_id, timestamp, amount, currency,
                            sender_account, receiver_account,
                            sender_country, sender_municipality,
                            receiver_country, receiver_municipality,
                            transaction_type, notes
                        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s);
                    """, (
                        row["transaction_id"], timestamp, amount, currency,
                        row["sender_account"], row["receiver_account"],
                        row["sender_country"], row["sender_municipality"],
                        row["receiver_country"], row["receiver_municipality"],
                        row["transaction_type"], row.get("notes", "")
                    ))

                except Exception as row_error:
                    logging.error(f"Fel i rad: {row_error}")
                    rejected_writer.writerow(row)

            conn.commit()
            logging.info("Import lyckades!")

    except Exception as e:
        conn.rollback()
        logging.error(f"Import misslyckades, rollback genomförd: {e}")

    finally:
        conn.close()
        logging.info("Program ended")

if __name__ == "__main__":
    main()
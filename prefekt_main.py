import logging
import psycopg2
import csv
from datetime import datetime
from contextlib import contextmanager
from db import init_db
from prefect import flow, task

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


@contextmanager
def get_db_connection():
    """Context manager för databasanslutning"""
    conn = None
    try:
        conn = psycopg2.connect(
            "dbname=transactions user=bankuser password=bankpass host=localhost port=5432"
        )
        yield conn
    except Exception as e:
        if conn:
            conn.rollback()
        raise e
    finally:
        if conn:
            conn.close()


def clean_amount(value):
    """Rensa och konvertera belopp"""
    if not value:
        return None
    value = value.replace(" ", "").replace(",", ".")
    try:
        return float(value)
    except ValueError:
        return None


def clean_timestamp(ts):
    """Rensa och formattera timestamp"""
    if not ts:
        return None
    formats = ["%Y-%m-%d %H:%M:%S", "%Y%m%d %H:%M:%S"]
    for fmt in formats:
        try:
            parsed = datetime.strptime(ts.strip(), fmt)
            return parsed.strftime("%Y-%m-%d %H:%M:%S")
        except ValueError:
            continue
    return None


def normalize_currency(currency):
    """Normalisera valutakod"""
    if not currency:
        return None
    code = currency.strip().upper()
    return "CNY" if code == "RMB" else code


def validate_and_clean_row(row):
    """Validera och rensa en rad data"""
    # Kontrollera obligatoriska fält
    for field in required_fields:
        if not row.get(field) or str(row[field]).strip() == "":
            raise ValueError(f"{field} saknar värde")

    # Rensa timestamp
    timestamp = clean_timestamp(row["timestamp"])
    if not timestamp:
        raise ValueError(f"Ogiltigt timestamp format: {row['timestamp']}")

    # Rensa belopp
    amount = clean_amount(row["amount"])
    if amount is None:
        raise ValueError(f"Ogiltigt belopp: {row['amount']}")

    # Rensa valuta
    currency = normalize_currency(row["currency"])
    if not currency:
        raise ValueError(f"Saknar eller ogiltig valuta: {row['currency']}")

    return {
        'transaction_id': row["transaction_id"],
        'timestamp': timestamp,
        'amount': amount,
        'currency': currency,
        'sender_account': row["sender_account"],
        'receiver_account': row["receiver_account"],
        'sender_country': row["sender_country"],
        'sender_municipality': row["sender_municipality"],
        'receiver_country': row["receiver_country"],
        'receiver_municipality': row["receiver_municipality"],
        'transaction_type': row["transaction_type"],
        'notes': row.get("notes", "")
    }


@task
def process_csv_file(file_path):
    """Läs och validera CSV-filen"""
    valid_rows = []
    rejected_rows = []

    try:
        with open(file_path, newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)

            for row_num, row in enumerate(reader, 1):
                try:
                    cleaned_row = validate_and_clean_row(row)
                    valid_rows.append(cleaned_row)
                except Exception as e:
                    logging.warning(f"Rad {row_num} avvisad: {e}")
                    row['rejection_reason'] = str(e)
                    rejected_rows.append(row)

    except Exception as e:
        logging.error(f"Fel vid läsning av CSV: {e}")
        raise

    logging.info(f"Behandlade {len(valid_rows)} giltiga rader, {len(rejected_rows)} avvisade")
    return valid_rows, rejected_rows


@task
def insert_transactions(valid_rows):
    """Infoga giltiga transaktioner i databasen"""
    inserted_count = 0

    with get_db_connection() as conn:
        cur = conn.cursor()

        try:
            for row in valid_rows:
                cur.execute("""
                            INSERT INTO transactions (transaction_id, timestamp, amount, currency,
                                                      sender_account, receiver_account,
                                                      sender_country, sender_municipality,
                                                      receiver_country, receiver_municipality,
                                                      transaction_type, notes)
                            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                            """, (
                                row['transaction_id'], row['timestamp'], row['amount'],
                                row['currency'], row['sender_account'], row['receiver_account'],
                                row['sender_country'], row['sender_municipality'],
                                row['receiver_country'], row['receiver_municipality'],
                                row['transaction_type'], row['notes']
                            ))
                inserted_count += 1

            conn.commit()
            logging.info(f"Infogade {inserted_count} transaktioner framgångsrikt")

        except Exception as e:
            conn.rollback()
            logging.error(f"Databasfel, rollback genomförd: {e}")
            raise

    return inserted_count


@task
def write_rejected_rows(rejected_rows, output_file):
    """Skriv avvisade rader till fil"""
    if not rejected_rows:
        return 0

    field_names = required_fields + ["notes", "rejection_reason"]

    try:
        with open(output_file, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=field_names)
            writer.writeheader()
            writer.writerows(rejected_rows)

        logging.info(f"Skrev {len(rejected_rows)} avvisade rader till {output_file}")
        return len(rejected_rows)

    except Exception as e:
        logging.error(f"Fel vid skrivning av avvisade rader: {e}")
        raise


@flow
def import_transactions(csv_file="transactions.csv", rejected_file="rejected_transactions.csv"):
    """Huvudflöde för import av transaktioner"""
    logging.info("Transaktionsimport startad")

    # Initiera databas
    init_db()

    try:
        # Bearbeta CSV-fil
        valid_rows, rejected_rows = process_csv_file(csv_file)

        # Infoga giltiga rader
        inserted_count = 0
        if valid_rows:
            inserted_count = insert_transactions(valid_rows)

        # Skriv avvisade rader
        rejected_count = 0
        if rejected_rows:
            rejected_count = write_rejected_rows(rejected_rows, rejected_file)

        logging.info(f"""
Import slutförd:
- {inserted_count} transaktioner infogade
- {rejected_count} rader avvisade
- Avvisade rader sparade i {rejected_file}
        """)

        return {
            'inserted': inserted_count,
            'rejected': rejected_count,
            'success': True
        }

    except Exception as e:
        logging.error(f"Import misslyckades: {e}")
        return {
            'inserted': 0,
            'rejected': 0,
            'success': False,
            'error': str(e)
        }


if __name__ == "__main__":
    result = import_transactions()
    if result['success']:
        logging.info("Program slutfört framgångsrikt")
    else:
        logging.error("Program slutfört med fel")
        exit(1)
import csv
import logging
import psycopg2
import datetime


# Logging-konfiguration
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)


required_fields = ["customer", "address", "phone", "personalnumber", "bankaccount"]

def import_customers(conn, filename="sebank_customers_with_accounts.csv"):
    cur = conn.cursor()

    try:
        with open(filename, newline='', encoding='utf-8') as f:
            reader = csv.DictReader(f)

            for row in reader:
                try:

                    row = {k.lower(): v for k, v in row.items()}

                    if "personnummer" in row:
                        row["personalnumber"] = row.pop("personnummer")

                    for field in required_fields:
                        if not row.get(field) or row[field].strip() == "":
                            raise ValueError(f"{field} is missing")


                    cur.execute("""
                        INSERT INTO customers (customer, address, phone, personalnumber, bankaccount)
                        VALUES (%s, %s, %s, %s, %s)
                    """, (
                        row["customer"],
                        row["address"],
                        row["phone"],
                        row["personalnumber"],
                        row["bankaccount"]
                    ))

                except Exception as row_error:
                    conn.rollback()
                    logging.error(f"Failed to insert row: {row}, Error: {row_error}")

        conn.commit()
        logging.info("Customer import complete.")

    except Exception as e:
        conn.rollback()
        logging.error(f"Customer import failed. Rollback performed: {e}")




import psycopg2
from db import init_db,session
import csv
from datetime import datetime


def main():
    init_db()



conn = psycopg2.connect("dbname=datakvalitet user=myuser password=mysecretpassword host=localhost port=5461")
cur = conn.cursor()

def clean_amount(value):
    if not value:
        return None

    value = value.replace(" ", "").replace(",", ".")
    try:
        return float(value)
    except ValueError:
        return None
def clean_timestamp(ts):
    """
    Försöker tolka olika timestamp-format och returnera i standardformat.
    """
    formats = ["%Y-%m-%d %H:%M:%S", "%Y%m%d %H:%M:%S"]
    for fmt in formats:
        try:
            parsed = datetime.strptime(ts.strip(), fmt)
            return parsed.strftime("%Y-%m-%d %H:%M:%S")  # Standardformat
        except ValueError:
            continue
    return None

try:
    with open("transactions.csv", newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        cur.execute("BEGIN;")

        for row in reader:
            try:
                datetime.strptime(row["timestamp"], "%Y-%m-%d %H:%M:%S")
            except ValueError:
                print("Ogiltigt timestamp format: " + row['timestamp'])

            timestamp = clean_timestamp(row["timestamp"])
            if not timestamp:
                print("Ogiltigt timestamp format: " + row['timestamp'])


            amount = clean_amount(row["amount"])

            cur.execute("INSERT INTO transactions (transaction_id, timestamp, amount, currency, sender_account, receiver_account, sender_country, sender_municipality, receiver_country, receiver_municipality, transaction_type, notes) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s);",
                        (row['transaction_id'], timestamp , amount, row["currency"], row["sender_account"], row["receiver_account"], row["sender_country"], row["sender_municipality"], row["receiver_country"], row["receiver_municipality"], row["transaction_type"], row["notes"]))
        conn.commit()
        print("Import lyckades!")

except Exception as e:
    conn.rollback()
    print("Import misslyckades, rollback genomförd:", e)

finally:
    conn.close()



if __name__ == "__main__":
    main()
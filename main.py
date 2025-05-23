import psycopg2
from db import init_db,session
import csv
from datetime import datetime
import os


def main():
    init_db()



conn = psycopg2.connect("dbname=datakvalitet user=myuser password=mysecretpassword host=localhost port=5461")
cur = conn.cursor()

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
                    if not row.get(field) or row[field] == "":
                        raise ValueError(f"{field} saknar värde")


                    timestamp = clean_timestamp(row["timestamp"])
                if not timestamp:
                    print("Ogiltigt timestamp format: " + row['timestamp'])

                amount = clean_amount(row["amount"])
                if amount is None:
                    raise ValueError(f"Ogiltigt belopp: {row['amount']}")

                currency = normalize_currency(row["currency"])
                if not currency:
                    raise ValueError(f"Saknar eller ogiltig valuta: {row['currency']}")


                cur.execute("INSERT INTO transactions (transaction_id, timestamp, amount, currency, sender_account, receiver_account, sender_country, sender_municipality, receiver_country, receiver_municipality, transaction_type, notes) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s);",
                        (row["transaction_id"], timestamp , amount, currency, row["sender_account"], row["receiver_account"], row["sender_country"], row["sender_municipality"], row["receiver_country"], row["receiver_municipality"], row["transaction_type"], row["notes"]))

            except Exception as row_error:
                print("Fel i rad", row_error)

                cleaned_row = {k: (", ".join(map(str, v)) if isinstance(v, list) else v) for k, v in row.items()}
                rejected_writer.writerow(cleaned_row)


        conn.commit()
        print("Import lyckades!")

except Exception as e:
    conn.rollback()
    print("Import misslyckades, rollback genomförd:", e)

finally:
    rejected_files.close()
    conn.close()



if __name__ == "__main__":
    main()
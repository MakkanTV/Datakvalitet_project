import csv
import psycopg2
from db import init_db, session


    #init_db()
    #db = session

    #customer = Customer(name ="Benjamin", ssn="9707278110", email="Tedgullander@gmail.com")
    #db.add(customer)
    #db.commit()

    #account = Account(name = "Ted", balance = 3000, customer_id=customer.id)
    #db.add(account)
    #db.commit()

    #print(f"customer: {customer.name} has balance: {Customer.balance}")

    #db.close()

conn = psycopg2.connect("dbname=account_customer user=myuser password=mysecretpassword host=localhost port=5461")
cur = conn.cursor()

#with open("customer.csv") as f:
    #reader = csv.reader(f)
    #for row in reader:
        #cur.execute("INSERT INTO customers(name, ssn, email) VALUES (%s, %s, %s)",
                    #(row[0], row[1], row[2]))

#conn.commit()
#cur.close()
#conn.close()

try:
    with open('customer.csv') as f:
        reader = csv.DictReader(f)
        cur.execute("BEGIN;")

        for row in reader:
            if not row['ssn'].isdigit():
                raise ValueError("Ogiltigt personnummer: " + row['ssn'])

            cur.execute("INSERT INTO customers (name, ssn, email) VALUES (%s, %s, %s);",
                        (row['name'], row['ssn'], row['email']))

            conn.commit()
            print("import successful")

except Exception as e:
    conn.rollback()
    print("Import misslyckades, rollback genomförd:", e)

finally:
    conn.close()
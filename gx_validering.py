import pandas as pd
import great_expectations as gx
import logging


# Konfigurera logging
logging.basicConfig(
    filename="validation.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

# Gamla versionen
def validate_transactions_csv(file_path):
    raw_df = pd.read_csv(file_path)
    print("Kolumner:", raw_df.columns.tolist())
    print("Dtypes:", raw_df.dtypes)

    # Förbered data
    raw_df["currency"] = raw_df["currency"].str.strip().str.upper()
    raw_df["amount"] = pd.to_numeric(raw_df["amount"], errors="coerce")

    df = gx.dataset.PandasDataset(raw_df)

    # Valideringar
    df.expect_column_values_to_not_be_null("transaction_id")
    df.expect_column_values_to_be_unique("transaction_id")
    df.expect_column_values_to_not_be_null("amount")
    df.expect_column_values_to_be_between("amount", min_value=0)
    df.expect_column_values_to_be_in_set("currency", ["SEK", "USD", "EUR"])

    # Radrapport
    raw_df["amount_not_null"] = ~raw_df["amount"].isnull()
    raw_df["amount_valid_range"] = raw_df["amount"] >= 0
    raw_df["currency_valid"] = raw_df["currency"].isin(["SEK", "USD", "EUR"])
    raw_df["valid"] = raw_df["amount_not_null"] & raw_df["amount_valid_range"] & raw_df["currency_valid"]

    # Spara
    raw_df.to_csv("validated_transactions.csv", index=False)
    raw_df[~raw_df["valid"]].to_csv("invalid_transactions.csv", index=False)
    raw_df[raw_df["valid"]].to_csv("valid_transactions.csv", index=False)

    print("Validering klar!")
    print(f"Alla rader: validated_transactions.csv")
    print(f"Felaktiga rader: invalid_transactions.csv")
    print(f"Korrekt data: valid_transactions.csv")

# Ny version med loggning och JSON-rapport
def validate_transactions_csv(file_path):
    raw_df = pd.read_csv(file_path)
    raw_df["currency"] = raw_df["currency"].str.strip().str.upper()
    raw_df["amount"] = pd.to_numeric(raw_df["amount"], errors="coerce")

    df = gx.dataset.PandasDataset(raw_df)

    validation_results = {
        "transaction_id_not_null": df.expect_column_values_to_not_be_null("transaction_id", result_format="COMPLETE"),
        "transaction_id_unique": df.expect_column_values_to_be_unique("transaction_id", result_format="COMPLETE"),
        "amount_not_null": df.expect_column_values_to_not_be_null("amount", result_format="COMPLETE"),
        "amount_positive": df.expect_column_values_to_be_between("amount", min_value=0, result_format="COMPLETE"),
        "currency_valid": df.expect_column_values_to_be_in_set("currency", ["SEK", "USD", "EUR"], result_format="COMPLETE")
    }

    # Logga
    logging.info("Valideringsresultat:")
    for key, value in validation_results.items():
        logging.info(f"{key}: {'✅' if value else '❌'}")


    # Spara CSV-filer
    raw_df.to_csv("validated_transactions.csv", index=False)


    print("Validering klar!")
    print("Logg sparad i validation.log")

# Använd ny version som standard
if __name__ == "__main__":
    validate_transactions_csv("transactions.csv")


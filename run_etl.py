from fetch_stock_data import fetch_all_stocks
from calculate_indicators import calculate_all_indicators


def run_etl():
    print("Starting ETL pipeline...")
    fetch_all_stocks()
    calculate_all_indicators()
    print("ETL pipeline completed successfully.")


if __name__ == "__main__":
    run_etl()

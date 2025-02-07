import os
import json
from scraper import get_dates_and_prices
from processor import process_data

def read_urls_from_json(json_file_path):
    print(f"Reading URLs from JSON file: {json_file_path}")
    with open(json_file_path, 'r', encoding='utf-8') as f:
        return json.load(f)

if __name__ == "__main__":
    json_file_name = "sources.json"
    json_file_path = os.path.join(os.pardir, json_file_name)
    url_data = read_urls_from_json(json_file_path)

    for name, details in url_data.items():
        link = details["link"]
        departure_from = details["departure_from"]

        print(f"\nReading data for {name}...")
        results = get_dates_and_prices(link, departure_from)

        print(f"\nFound departure dates for {name}:")
        for term, price in results:
            print(f"{term}: {price} zł")

        print(f"\nEnsuring that the 'data' directory exists...")
        if not os.path.exists("data"):
            os.makedirs("data")

        file_path = os.path.join(os.pardir, "data", f"{name}.csv")
        process_data(results, file_path)
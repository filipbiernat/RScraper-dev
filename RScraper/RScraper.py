import os
import json
from scraper import get_dates_and_prices
from processor import process_data

# Get the directory where the script is located
script_dir = os.path.dirname(os.path.abspath(__file__))

# Get the parent directory (one level up)
parent_dir = os.path.dirname(script_dir)

def read_urls_from_json(json_file_path):
    print(f"Reading URLs from JSON file: {json_file_path}")
    with open(json_file_path, 'r', encoding='utf-8') as f:
        return json.load(f)

if __name__ == "__main__":
    json_file_name = "sources.json"

    # The JSON file is located in the parent directory
    json_file_path = os.path.join(parent_dir, json_file_name)

    url_data = read_urls_from_json(json_file_path)

    for name, details in url_data.items():
        link = details["link"]
        departure_from = details["departure_from"]

        print(f"\nReading data for {name}...")
        results = get_dates_and_prices(link, departure_from)

        print(f"\nFound departure dates for {name}:")
        for term, price in results:
            print(f"{term}: {price} zł")

        # Ensure the "data" directory exists in the parent directory
        data_dir = os.path.join(parent_dir, "data")
        if not os.path.exists(data_dir):
            print(f"\nCreating directory: {data_dir}")
            os.makedirs(data_dir)
        else:
            print(f"\nDirectory already exists: {data_dir}")

        file_path = os.path.join(data_dir, f"{name}.csv")
        print(f"Saving data to: {file_path}")

        process_data(results, file_path)

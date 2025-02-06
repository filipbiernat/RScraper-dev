import os
import json
from scraper import get_dates_and_prices
from processor import process_data

def read_urls_from_json(json_file):
    print(f"Reading URLs from JSON file: {json_file}")
    with open(json_file, 'r', encoding='utf-8') as f:
        return json.load(f)

if __name__ == "__main__":
    json_file = "sources.json"
    url_data = read_urls_from_json(json_file)
    
    for name, url in url_data.items():
        print(f"\nReading data for {name}...")
        results = get_dates_and_prices(url)
        
        print(f"\nFound departure dates for {name}:")
        for term, price in results:
            print(f"{term}: {price} zł")

        print(f"\nEnsuring that the 'data' directory exists...")
        if not os.path.exists("data"):
            os.makedirs("data")

        file_path = os.path.join("data", f"{name}.csv")
        process_data(results, file_path)
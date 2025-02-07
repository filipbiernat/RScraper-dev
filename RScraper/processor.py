import os
import csv
from datetime import datetime

def get_current_timestamp():
    current_time = datetime.now()
    timestamp = current_time.strftime("%d.%m.%Y %H:%M:%S")
    print(f"Current timestamp: {timestamp}")
    return timestamp

def load_existing_prices(file_path):
    print(f"Loading existing prices from file: {file_path}")
    existing_prices = {}
    if not os.path.exists(file_path):
        print(f"File {file_path} does not exist. Returning an empty dictionary.")
        return existing_prices
    
    with open(file_path, 'r', encoding='utf-8') as file:
        lines = file.readlines()
        if len(lines) == 0:
            print(f"File {file_path} is empty. Returning an empty dictionary.")
            return existing_prices
        
        headers = lines[0].strip().split(',')
        if len(headers) <= 1:
            print(f"Headers in {file_path} are invalid. Returning an empty dictionary.")
            return existing_prices
        
        headers = headers[1:]
        for line in lines[1:]:
            parts = line.strip().split(',')
            if len(parts) < 2:
                continue
            
            term = parts[0]
            existing_prices[term] = {}
            
            for i, price in enumerate(parts[1:]):
                if i >= len(headers):
                    continue
                
                timestamp = headers[i]
                existing_prices[term][timestamp] = int(price) if price else None
    
    return existing_prices

def build_new_prices(results):
    print("Building new prices...")
    new_prices = {}
    current_timestamp = get_current_timestamp()
    
    for term, price in results:
        if term not in new_prices:
            new_prices[term] = {}
        new_prices[term][current_timestamp] = int(price)
    
    return new_prices

def merge_prices(existing_prices, new_prices):
    print("Merging existing and new prices...")
    for term, timestamps in new_prices.items():
        if term in existing_prices:
            existing_prices[term].update(timestamps)
        else:
            existing_prices[term] = timestamps
    return existing_prices

def parse_date_from_term(term):
    today = datetime.today()
    
    # Extract the start date from the format "dd.mm - dd.mm"
    start_date_str = term.split(' - ')[0]
    parsed_date = datetime.strptime(start_date_str, "%d.%m")
    
    # Assign the current year
    full_date = parsed_date.replace(year=today.year)
    
    # If the date is in the past, assign the next year
    if full_date < today:
        full_date = full_date.replace(year=today.year + 1)
    
    return full_date

def save_prices_to_csv(prices, file_path):
    print(f"Saving merged prices to CSV file: {file_path}")
    with open(file_path, 'w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        timestamps = set()
        for term, timestamps_prices in prices.items():
            timestamps.update(timestamps_prices.keys())
        
        sorted_timestamps = sorted(timestamps)
        writer.writerow([''] + sorted_timestamps)
        
        print(f"Sorting the dates in ascending order by the start date")
        sorted_terms = sorted(prices.keys(), key=parse_date_from_term)
        
        print(f"Building the output file: {file_path}")

        for term in sorted_terms:
            row = [term]
            for timestamp in sorted_timestamps:
                row.append(prices[term].get(timestamp, ''))
            writer.writerow(row)
    print(f"Merged data saved to: '{file_path}'")

def process_data(results, file_path):
    existing_prices = load_existing_prices(file_path)
    new_prices = build_new_prices(results)
    merged_prices = merge_prices(existing_prices, new_prices)
    save_prices_to_csv(merged_prices, file_path)

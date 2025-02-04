import re
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import platform
import os
from datetime import datetime
import csv
import json

def get_dates_and_prices(url):
    IS_IN_BACKGROUND = True
    IS_WINDOWS = platform.system() == "Windows"
    
    def configure_driver():
        print("Configuring WebDriver...")
        options = Options()
        if IS_IN_BACKGROUND:
            options.add_argument("--headless")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        chromedriver_path = "C:/chromedriver-win64/chromedriver.exe" if IS_WINDOWS else "/usr/local/bin/chromedriver"
        service = Service(chromedriver_path)
        
        if not IS_WINDOWS:
            options.binary_location = "/usr/bin/chromium-browser"
        
        print(f"Using chromedriver path: {chromedriver_path}")
        return webdriver.Chrome(options=options)
    
    def click_button(driver, xpath, description, timeout=20):
        print(f"Attempting to click button: {description}")
        try:
            button = WebDriverWait(driver, timeout).until(
                EC.element_to_be_clickable((By.XPATH, xpath))
            )
            button.click()
            print(f"Button '{description}' clicked successfully.")
        except Exception as e:
            with open("page_source.html", "w", encoding='utf-8') as f:
                f.write(driver.page_source) # Save page source for debugging
            driver.quit()
            print(f"Error clicking button '{description}': {e}")
            raise Exception(f"Button '{description}' not found: {e}")
    
    def extract_text(driver, xpath, description, timeout=10):
        print(f"Attempting to extract text from: {description}")
        try:
            element = WebDriverWait(driver, timeout).until(
                EC.presence_of_element_located((By.XPATH, xpath))
            )
            text = element.text.strip()
            print(f"Text extracted from '{description}': {text[:100]}...")  # print first 100 chars
            return text
        except Exception as e:
            print(f"Error extracting text from '{description}': {e}")
            return None
    
    def parse_dates_and_prices(text):
        print("Parsing dates and prices from extracted text...")
        regex = r"(\d{2}\.\d{2} - \d{2}\.\d{2}).*?\n([\d\s]+)zł"
        matches = re.finditer(regex, text, re.DOTALL)
        parsed_data = [(match.group(1), match.group(2).replace(" ", "").replace("\n", "")) for match in matches]
        print(f"Parsed data: {parsed_data}")
        return parsed_data
    
    print(f"Opening URL: {url}")
    driver = configure_driver()
    driver.get(url)
    
    WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.TAG_NAME, 'body')))
    
    print("Waiting for page to load...")
    click_button(driver, "//button[contains(., 'Akceptuj wszystkie')]" , "Akceptuj wszystkie")
    click_button(driver, "//button[contains(@class, 'r-select-button-termin')]", "r-select-button-termin")
    click_button(driver, "//button[contains(., 'Lista')]", "Lista")
    
    date_list_xpath = "//div[contains(@class, 'kh-terminy-list')]"
    date_list_text = extract_text(driver, date_list_xpath, "Departure dates list")
    
    driver.quit()
    
    if date_list_text:
        return parse_dates_and_prices(date_list_text)
    return []

def process_data(results, file_path):
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

    def save_prices_to_csv(prices, file_path):
        print(f"Saving merged prices to CSV file: {file_path}")
        with open(file_path, 'w', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            timestamps = set()
            for term, timestamps_prices in prices.items():
                timestamps.update(timestamps_prices.keys())
            
            sorted_timestamps = sorted(timestamps)
            writer.writerow([''] + sorted_timestamps)
            
            for term, timestamps_prices in prices.items():
                row = [term]
                for timestamp in sorted_timestamps:
                    row.append(timestamps_prices.get(timestamp, ''))
                writer.writerow(row)
        print(f"Merged data saved to '{file_path}'")

    existing_prices = load_existing_prices(file_path)
    new_prices = build_new_prices(results)
    merged_prices = merge_prices(existing_prices, new_prices)
    save_prices_to_csv(merged_prices, file_path)

def read_urls_from_json(json_file):
    print(f"Reading URLs from JSON file: {json_file}")
    with open(json_file, 'r', encoding='utf-8') as f:
        return json.load(f)

if __name__ == "__main__":
    # Loading data from JSON file
    json_file = "sources.json"
    url_data = read_urls_from_json(json_file)
    
    for name, url in url_data.items():
        print(f"\nReading data for {name}...")
        results = get_dates_and_prices(url)
        
        print(f"\nFound departure dates for {name}:")
        for term, price in results:
            print(f"{term}: {price} zł")
        
        # Generating CSV file path in 'data' folder
        file_path = os.path.join("data", f"{name}.csv")
        process_data(results, file_path)

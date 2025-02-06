import re
import platform
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

IS_IN_BACKGROUND = True
IS_WINDOWS = platform.system() == "Windows"

def configure_driver():
    print("Configuring WebDriver...")
    options = Options()
    if IS_IN_BACKGROUND:
        options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    
    if not IS_WINDOWS:
        options.binary_location = "/usr/bin/chromium-browser"
    
    return webdriver.Chrome(options=options)

def click_button(driver, description, xpath_fragment, timeout=20):
    print(f"Attempting to click button: {description}")
    try:
        full_xpath = f"//button{xpath_fragment}"
        button = WebDriverWait(driver, timeout).until(
            EC.element_to_be_clickable((By.XPATH, full_xpath))
        )
        button.click()
        print(f"Button '{description}' clicked successfully.")
    except Exception as e:
        driver.quit()
        print(f"Error clicking button '{description}': {e}")
        raise Exception(f"Button '{description}' not found: {e}.")

def extract_text(driver, xpath, description, timeout=10):
    print(f"Attempting to extract text from: {description}")
    try:
        element = WebDriverWait(driver, timeout).until(
            EC.presence_of_element_located((By.XPATH, xpath))
        )
        text = element.text.strip()
        print(f"Text extracted from '{description}': {text[:100]}...")
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

def get_dates_and_prices(url):
    print(f"Opening URL: {url}")
    driver = configure_driver()
    driver.get(url)
    
    WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.TAG_NAME, 'body')))
    
    print("Waiting for page to load...")
    click_button(driver, "Akceptuj wszystkie", "[contains(., 'Akceptuj wszystkie')]")
    click_button(driver, "r-select-button-termin", "[contains(@class, 'r-select-button-termin')]")
    click_button(driver, "Lista", "[@data-test-id='r-tab:kartaHotelu-konfigurator-termin:1']")
    
    date_list_xpath = "//div[contains(@class, 'kh-terminy-list')]"
    date_list_text = extract_text(driver, date_list_xpath, "Departure dates list")
    
    driver.quit()
    
    if date_list_text:
        return parse_dates_and_prices(date_list_text)
    return []
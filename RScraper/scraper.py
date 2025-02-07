import re
import platform
import time
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

def click_button(driver, description, xpath, timeout=20):
    print(f"Attempting to click button: {description}")
    try:
        # Ensure the button is clickable
        xpath_element = (By.XPATH, xpath)
        button = WebDriverWait(driver, timeout).until(
            EC.element_to_be_clickable(xpath_element)
        )

        # Click
        button.click()
        print(f"Button '{description}' clicked successfully.")
    except Exception as e:
        driver.quit()
        print(f"Error clicking button '{description}': {e}")
        raise Exception(f"Button '{description}' not found: {e}.")

def click_div(driver, description, xpath, timeout=20):
    print(f"Attempting to click on DIV block: {description}")
    try:
        # Ensure the DIV block is visible
        xpath_element = (By.XPATH, xpath)
        located_div_block = WebDriverWait(driver, timeout).until(
            EC.presence_of_element_located(xpath_element)
        )
        driver.execute_script("arguments[0].scrollIntoView();", located_div_block)

        # Ensure the DIV block is clickable
        clickable_div_block = WebDriverWait(driver, timeout).until(
            EC.element_to_be_clickable(located_div_block)
        )

        # Click
        driver.execute_script("arguments[0].click();", clickable_div_block)
        print(f"DIV block '{description}' clicked successfully.")
    except Exception as e:
        driver.quit()
        print(f"Error clicking on DIV block '{description}': {e}")
        raise Exception(f"DIV block '{description}' not found: {e}.")

def wait_for_loader_to_disappear(driver, timeout=20):
    print("Waiting for the loader to disappear")
    try:
        loader_xpath = "//div[contains(@class, 'r-loader')]"
        WebDriverWait(driver, timeout).until(
            EC.invisibility_of_element_located((By.XPATH, loader_xpath))
        )
        print("Loader disappeared, proceeding with click.")
    except Exception as e:
        print(f"Error while waiting for loader: {e}")
        raise


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

def get_dates_and_prices(url, departure_from):
    print(f"Opening URL: {url}")
    driver = configure_driver()
    driver.get(url)
    
    WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.TAG_NAME, 'body')))
    
    print("Waiting for page to load...")
    click_button(driver, "Akceptuj wszystkie", "//button[contains(., 'Akceptuj wszystkie')]")


    click_button(driver, "Miejsce wylotu", "//button[@data-test-id='r-select-button:kartaHotelu-konfigurator:polaczenie']")
    click_div(driver, departure_from, f"//div[contains(., '{departure_from}') and contains(@data-test-id, 'r-component:pojedyncze-polaczenie:container')]")
    wait_for_loader_to_disappear(driver)

    click_button(driver, "Termin", "//button[contains(@class, 'r-select-button-termin')]")
    click_button(driver, "Lista", "//button[@data-test-id='r-tab:kartaHotelu-konfigurator-termin:1']")

    print("Extracting text...")
    date_list_xpath = "//div[contains(@class, 'kh-terminy-list')]"
    date_list_text = extract_text(driver, date_list_xpath, "Departure dates list")
    
    driver.quit()
    
    if date_list_text:
        return parse_dates_and_prices(date_list_text)
    return []
"""Selenium (uc) script for pulling prices (no API sites)"""

import sys
import time

import undetected_chromedriver as uc
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from sqlalchemy import select
from sqlalchemy.orm import Session

from inventory_inserter import create_and_return_db_engine
from app import Inventory



class DriverSelection:
    CHROME = "chrome"
    FIREFOX = "firefox"

class PricingMethod:
    AVG = "avg"
    MIN = "min"
    MAX = "max"

def create_and_return_driver(which_driver=DriverSelection.FIREFOX, run_headless=False):
    if which_driver == DriverSelection.CHROME:
        driver = uc.Chrome(headless=run_headless)

    elif which_driver == DriverSelection.FIREFOX:
        driver = webdriver.Firefox()
    return driver

def get_fetch_urls_and_row_data():
    db_engine = create_and_return_db_engine()

    stmt = select(Inventory.check_price_url, Inventory.row).where(Inventory.check_price_url != None)

    urls_and_rows = []

    with db_engine.connect() as conn:
        for result in conn.execute(stmt):
            urls_and_rows.append(list(result))

    return urls_and_rows

    
def fetch_prices_and_update_db(fetch_urls_and_rows, pricing_method):
    driver = create_and_return_driver()

    wait = WebDriverWait(driver, 60)  # NOTE: Keep this wait time high for now, browser may be slow to load

    #try:

    for event_data in fetch_urls_and_rows:
        url, row = event_data

        driver.get(url)

        wait.until(EC.url_to_be(url))

        print("Page Successfully Loaded")

        # Scrape the price
        listing_container = wait.until(EC.presence_of_element_located((By.XPATH, "//div[@class='listing-container']")))
        print("Listing Container Found")

        listing_elements = listing_container.find_elements(By.XPATH, "//div[@class='listing']")

        # NOTE: Logic will differ depending on whether row is 'GA' or not
        if row == 'ga':
            print("Event is GA")

            if pricing_method == PricingMethod.AVG:
                raw_prices = [listing.find_element(By.XPATH, "//label/b[1]").text for listing in listing_elements]
                print(raw_prices)
                #avg_price = sum(prices) / len(prices)
                #print(f"Average Price: {avg_price}")



        else:
            print("Event is not GA")

        # Update the price in the database

    driver.quit()

    #except Exception as e:
        #print(f"An error occurred: {e}")
        #driver.quit()

def run_fetch_process(pricing_method=PricingMethod.AVG):
    fetch_urls_and_rows = get_fetch_urls_and_row_data()

    fetch_prices_and_update_db(fetch_urls_and_rows, pricing_method)
    print("Price fetch process complete.")


if __name__ == "__main__":
    run_fetch_process()

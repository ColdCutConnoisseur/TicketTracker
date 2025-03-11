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

from db_interface import create_and_return_db_engine, check_for_existing_datapoint_and_add_if_necessary
from app import Inventory

class NoPricingDataFound(Exception):
    pass

class NoSupplyDataFound(Exception):
    pass

class DriverSelection:
    CHROME = "chrome"
    FIREFOX = "firefox"

class PricingMethod:
    FTA = "fta" # First Three Average
    AVG = "avg"
    MIN = "min"
    MAX = "max"

def create_and_return_driver(which_driver=DriverSelection.FIREFOX, run_headless=False):
    if which_driver == DriverSelection.CHROME:
        driver = uc.Chrome(headless=run_headless)

    elif which_driver == DriverSelection.FIREFOX:
        driver = webdriver.Firefox()
    return driver

def fetch_event_data():
    db_engine = create_and_return_db_engine()

    stmt = select(Inventory.event_id, Inventory.check_price_url, Inventory.section, Inventory.row).where(Inventory.check_price_url != None)

    event_data = []

    with db_engine.connect() as conn:
        for result in conn.execute(stmt):
            event_data.append(list(result))

    return event_data

def fetch_event_pricing_data(driver, event_data_chunk, wait, pricing_method):
    event_id, url, section, row = event_data_chunk

    driver.get(url)

    wait.until(EC.url_to_be(url))

    print("Page Successfully Loaded")

    # Scrape the price
    listing_container = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "#listingContainer")))
    print("Listing Container Found")

    # BUG: Listing container will be loaded even when listings aren't loaded yet

    listings_loaded = False
    timeout_counter = 0
    timeouts_allowed = 6

    while not listings_loaded:

        if timeout_counter >= timeouts_allowed:
            #print("Timeouts exceeded. Exiting...")
            return (NoSupplyDataFound, NoPricingDataFound)

        try:
            listing_container.find_element(By.CLASS_NAME, "listing")
            listings_loaded = True

        except:
            print("Listings not loaded yet, waiting...")
            timeout_counter += 1
            time.sleep(5)

    listing_elements = listing_container.find_elements(By.CLASS_NAME, "listing")

    # TODO: Add a 'supply' table in database and track this info as 'section_supply' and consider 'total_event_supply'
    section_supply = len(listing_elements)
    print(f"Found {section_supply} listings.")

    # NOTE: Logic will differ depending on whether row is 'GA' or not
    if row == 'ga':
        print("Event is GA")

        # Scrape Prices
        raw_prices = [listing.find_element(By.XPATH, "./label/b[1]").text for listing in listing_elements]
        raw_prices = [price.replace(",", "") for price in raw_prices]
        prices = [float(price.replace("$", "")) for price in raw_prices]

        if pricing_method == PricingMethod.AVG:
            
            avg_price = sum(prices) / len(prices)
            print(f"Average Price: {avg_price}")

            return (section_supply, avg_price)
        
        elif pricing_method == PricingMethod.MIN:
            
            min_price = min(prices)
            print(f"Min Price: {min_price}")

            return (section_supply, min_price)
        
        elif pricing_method == PricingMethod.MAX:
            
            max_price = max(prices)
            print(f"Max Price: {max_price}")

            return (section_supply, max_price)
        
        elif pricing_method == PricingMethod.FTA:
            
            first_three_prices = prices[:3]
            fta_avg = sum(first_three_prices) / len(first_three_prices)
            print(f"First Three Average Price: ${fta_avg:.2f}")

            return (section_supply, fta_avg)

    else:
        print("Event is not GA")

def fetch_prices_and_update_db(event_data, pricing_method):
    driver = create_and_return_driver()

    wait = WebDriverWait(driver, 12)  # NOTE: Keep this wait time high for now, browser may be slow to load

    #try:

    for data_chunk in event_data:
        event_id = data_chunk[0]
        url = data_chunk[1]
        event_section = data_chunk[2]
        event_row = data_chunk[3]

        section_supply, event_pricing = fetch_event_pricing_data(driver, data_chunk, wait, pricing_method)

        if section_supply is NoSupplyDataFound or event_pricing is NoPricingDataFound:
            print("No supply or pricing data found. Skipping...")
            continue
            
        else:
            print("Supply and pricing data found. Updating database...")
            # Insert data into 'Price' table

            check_for_existing_datapoint_and_add_if_necessary(event_id, event_section, event_row, event_pricing, url, section_supply)

    driver.quit()

    #except Exception as e:
        #print(f"An error occurred: {e}")
        #driver.quit()

def run_fetch_process(pricing_method=PricingMethod.AVG):
    event_data = fetch_event_data()

    fetch_prices_and_update_db(event_data, pricing_method)
    print("Price fetch process complete.")


if __name__ == "__main__":
    PRICING_METHOD = PricingMethod.FTA

    run_fetch_process(pricing_method=PRICING_METHOD)

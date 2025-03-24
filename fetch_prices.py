"""Selenium (uc) script for pulling prices (non-API sites)"""

import sys
import re
import time

import undetected_chromedriver as uc
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
#from selenium.webdriver import FirefoxOptions
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException, NoSuchElementException
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
    """Create and return selected driver and setting headless option"""
    
    if which_driver == DriverSelection.CHROME:
        driver = uc.Chrome(headless=run_headless)

    elif which_driver == DriverSelection.FIREFOX:
        print("Running FF Driver")
        options = Options()

        if run_headless:
            options.add_argument('--headless')
            print("Running browser headless")

        driver = webdriver.Firefox(options=options)

    return driver

def fetch_event_data():
    """DB fetch to get events that have not occurred yet"""
    db_engine = create_and_return_db_engine()

    stmt = select(Inventory.event_id, Inventory.check_price_url, Inventory.section, Inventory.row).where(Inventory.check_price_url != None)

    event_data = []

    with db_engine.connect() as conn:
        for result in conn.execute(stmt):
            event_data.append(list(result))

    return event_data

def look_for_and_return_listing_container(driver, wait):
    try:
        listing_container = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "#listingContainer")))
        print("Listing Container Found")
        return listing_container

    except TimeoutException:
        print("Timeout caught!  This could be cloudflare...")
        print("Taking screenshot...")
        driver.save_screenshot("page_arrival.png")
        print("Screenshot saved!")
        print("Exiting...")
        driver.quit()
        sys.exit(0)

def fetch_event_pricing_data(driver, event_data_chunk, wait, pricing_method):
    # TODO: This is a gimungo function -- Clean it up!!
    event_id, url, section, row = event_data_chunk
    print(f"Fetching event pricing for event:  << {event_id} >>...")

    driver.get(url)

    wait.until(EC.url_to_be(url))
    print("Page Successfully Loaded")

    listing_container = look_for_and_return_listing_container(driver, wait)

    listings_loaded = False
    timeout_counter = 0
    timeouts_allowed = 6

    while not listings_loaded:

        if timeout_counter >= timeouts_allowed:
            print("Timeouts exceeded. Exiting...")
            return (NoSupplyDataFound, NoPricingDataFound)

        try:
            listing_container.find_element(By.CLASS_NAME, "listing")
            listings_loaded = True

        except:
            print("Listings not loaded yet, waiting...")
            timeout_counter += 1
            time.sleep(4)

    # BUG: There are instances where the listing_container is found, the listings exist, but the prices are not loaded yet
    # NOTE: this still exists on slow connections!

    print("Sleeping to allow prices to populate...")
    time.sleep(5)  # Another arbitrary sleep -- hope that prices populate in listings
    print("Sleep exited.")

    listing_elements = listing_container.find_elements(By.CLASS_NAME, "listing")

    # TODO: Add a 'supply' table in database and track this info as 'section_supply' and consider 'total_event_supply'
    # NOTE: This was originally an idea but has been implemented somewhat by tracking supply info in the pricing table for time being
    listings_count = len(listing_elements)
    print(f"Found {listings_count} individual listings.")

    # Get number of tickets available per listing
    raw_quantities = [listing.find_element(By.XPATH, "./div[1]/select/option").get_attribute("value") for listing in listing elements]
    quantities_as_int = [int(q) for q in raw_quantities]
    section_supply = sum(quantities_as_int)

    print(f"Section supply: {section_supply}")

    # Scrape Prices
    raw_prices = [listing.find_element(By.XPATH, "./label/b[1]").text for listing in listing_elements]
    raw_prices = [price.replace(",", "") for price in raw_prices]
    prices = [float(price.replace("$", "")) for price in raw_prices]

    rows = [listing.find_element(By.XPATH, "./div[@class='details']/div/span").text for listing in listing_elements]

    # NOTE: Calculation logic will differ depending on whether row is 'GA' or not
    if row == 'ga':
        print("Event is GA")

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

        # NOTE: No guarantees that 'Row' text will exist for below regex!

        # Match tickets to row
        matched_prices = []
        row_regex = r'Row ([A-Z0-9]+)'
        revised_rows = [m.group(1) for m in [re.search(row_regex, row) for row in rows] if m is not None]

        for p, r in zip(prices, revised_rows):
            print(f"Price: {p}, Row: {r}")

            if r.lower() == row.lower():  # Standardize
                print("Row Matched")
                matched_prices.append(p)

        # After checking for matches, check len of matched list
        if len(matched_prices) < 1:
            print("No prices matched to row. Populating with section prices instead...")
            matched_prices = prices

        # And now caclulate avg/min/max/fta etc
        if pricing_method == PricingMethod.AVG:
            
            avg_price = sum(matched_prices) / len(matched_prices)
            print(f"Average Price: {avg_price}")

            return (section_supply, avg_price)
        
        elif pricing_method == PricingMethod.MIN:
            
            min_price = min(matched_prices)
            print(f"Min Price: {min_price}")

            return (section_supply, min_price)
        
        elif pricing_method == PricingMethod.MAX:
            
            max_price = max(matched_prices)
            print(f"Max Price: {max_price}")

            return (section_supply, max_price)
        
        elif pricing_method == PricingMethod.FTA:
            
            first_three_prices = matched_prices[:3]
            fta_avg = sum(first_three_prices) / len(first_three_prices)
            print(f"First Three Average Price: ${fta_avg:.2f}")

            return (section_supply, fta_avg)

def fetch_prices_and_update_db(driver_type, as_headless, event_data, pricing_method):
    for data_chunk in event_data:
        driver = create_and_return_driver(which_driver=driver_type, run_headless=as_headless)
        wait = WebDriverWait(driver, 90)
        event_id = data_chunk[0]
        url = data_chunk[1]
        event_section = data_chunk[2]
        event_row = data_chunk[3]

        # TODO: To save time, run the insert checks here
        # A.k.a if a datapoint already exists for today, skip that event scrape

        section_supply, event_pricing = fetch_event_pricing_data(driver, data_chunk, wait, pricing_method)

        if section_supply is NoSupplyDataFound or event_pricing is NoPricingDataFound:
            print("No supply or pricing data found. Skipping...")
            continue
            
        else:
            print("Supply and pricing data found. Updating database...")
            # Insert data into 'Price' table
            # TODO: Take check logic from this function for above TODO
            check_for_existing_datapoint_and_add_if_necessary(event_id, event_section, event_row, event_pricing, url, section_supply)

        driver.quit()

def run_fetch_process(driver_type=DriverSelection.FIREFOX, as_headless=False, pricing_method=PricingMethod.AVG):
    """Main function to run the fetch process--get data then insert it"""
    event_data = fetch_event_data()
    fetch_prices_and_update_db(driver_type, as_headless, event_data, pricing_method)
    print("Price fetch process complete.")


if __name__ == "__main__":
    # Config
    DRIVER_TYPE = DriverSelection.FIREFOX
    AS_HEADLESS = True
    PRICING_METHOD = PricingMethod.FTA

    # Run
    run_fetch_process(driver_type=DRIVER_TYPE, as_headless=AS_HEADLESS, pricing_method=PRICING_METHOD)

    # NOTE:  Where this stands:  UC does not load pages properly when run with browser, it gets flagged for cloudflare in headless,
    # Firefox works locally, but gets flagged by cloudflare on PA.

    # Seems like proxy is the only way to get around this -- not willing to put in that effort at this point

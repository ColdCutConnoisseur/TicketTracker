"""Helpers for setting up the initial 'inventory' table"""

import csv

import pandas as pd

from db_interface import create_and_return_db_engine

pd.set_option('display.max_columns', None)



def open_and_read_inventory_file(file_path: str) -> list[list]:
    inventory = []

    with open(file_path, 'r') as csv_in:
        csv_reader = csv.reader(csv_in)

        for line in csv_reader:
            inventory.append(line)

    return inventory[1:] # skip headers row


def load_inventory_w_pandas(file_path: str) -> pd.DataFrame:
    """type data for use with pandas"""
    types_dict = {
                    "event_id" : 'UInt16',
                    "event_name" : 'string',
                    "venue" : 'string',
                    "event_date" : 'string',
                    "event_time" : 'string',
                    "date_purchased" : 'string',
                    "qty_purchased" : 'float64',
                    "total_cost" : 'float64',
                    "cost_per" : 'float64',
                    "section" : 'string',
                    "row" : 'string',
                    "seat" : 'string',
                    "sale_payout_date" : 'string',
                    "self_use_qty" : 'UInt8',
                    "sale_total_proceeds" : 'float64',
                    "sale_marketplace" : 'string',
                    "notes" : 'string',
                    "manual_price_track" : 'float64',
                    "check_price_url" : 'string'
                   }

    df = pd.read_csv(filepath_or_buffer=file_path,
                               dtype=types_dict,
                               parse_dates=True)

    # Now do translations
    df["event_date"] = pd.to_datetime(df["event_date"], format="mixed")
    df["event_time"] = pd.to_datetime(df["event_time"], format="%H:%M:%S %p").dt.time
    df["date_purchased"] = pd.to_datetime(df["date_purchased"], format="mixed")
    df["sale_payout_date"] = pd.to_datetime(df["sale_payout_date"], format="mixed")

    return df

def add_inventory_to_db(inv_df: pd.DataFrame) -> None:
    """insert inventory items"""
    engine = create_and_return_db_engine()
    inv_df.to_sql('inventory', engine, if_exists='append', index=False)


if __name__ == "__main__":
    new_inv = load_inventory_w_pandas("./ticket_inventory.csv")
    add_inventory_to_db(new_inv)

    print("Inventory Added!")

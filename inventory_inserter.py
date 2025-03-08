

import os
import csv
import datetime

import pandas as pd
from sqlalchemy import create_engine

from config import SQLITE_DB_PATH

pd.set_option('display.max_columns', None)



def open_and_read_inventory_file(file_path: str) -> list[list]:
    inventory = []

    with open(file_path, 'r') as csv_in:
        csv_reader = csv.reader(csv_in)

        for line in csv_reader:
            inventory.append(line)

    return inventory[1:] # skip headers row


def load_inventory_w_pandas(file_path: str) -> pd.DataFrame:
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

def create_and_return_db_engine():
    engine = create_engine(SQLITE_DB_PATH)
    return engine

def add_inventory_to_db(inv_df: pd.DataFrame) -> None:
    engine = create_and_return_db_engine()
    inv_df.to_sql('inventory', engine, if_exists='append', index=False)


if __name__ == "__main__":
    #inventory = open_and_read_inventory_file("./ticket_inventory.csv")

    #print(inventory)

    new_inv = load_inventory_w_pandas("./ticket_inventory.csv")
    add_inventory_to_db(new_inv)

    print("Inventory Added!")

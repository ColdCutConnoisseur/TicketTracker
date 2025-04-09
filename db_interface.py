"""Functionality for interacting with the SQLite database"""

import sys
import datetime
from decimal import Decimal
from sqlalchemy import create_engine, text
from sqlalchemy.orm import Session

from config import MY_DB
from app import PriceDatapoint, Inventory

COMMIT_CHANGES = True


def create_and_return_db_engine():
    engine = create_engine(MY_DB)
    return engine

def create_inventory_item(event_name: str, venue: str, event_date: datetime.datetime,
                             event_time: datetime.time, date_purchased: datetime.datetime,
                             qty_purchased: float, total_cost: Decimal, cost_per: Decimal,
                             section: str, row: str, seat: str, sale_payout_date: datetime.datetime=None,
                             self_use_qty: int=0, sale_total_proceeds: Decimal=Decimal(0.0),
                             sale_marketplace: str='', notes: str='', manual_price_track: float=0.0,
                             check_price_url: str=''):
    engine = create_and_return_db_engine()

    with Session(engine) as session:

        new_inventory = Inventory(
            event_name = event_name,
            venue = venue,
            event_date = event_date,
            event_time = event_time,
            date_purchased = date_purchased,
            qty_purchased = qty_purchased,
            total_cost = total_cost,
            cost_per = cost_per,
            section = section,
            row = row,
            seat = seat,
            sale_payout_date = sale_payout_date,
            self_use_qty = self_use_qty,
            sale_total_proceeds = sale_total_proceeds,
            sale_marketplace = sale_marketplace,
            notes = notes,
            manual_price_track = manual_price_track,
            check_price_url = check_price_url
        )

        session.add(new_inventory)
        session.commit()

    engine.dispose()

def price_datapoint_exists_for_today(session: Session, event_id: int) -> bool:
    """Limit datapoints to max one observation per day"""
    # most_recent = session.execute(text(f"SELECT * FROM prices WHERE event_id = {event_id} ORDER BY observation_timestamp DESC LIMIT 1")).fetchone()
    most_recent = session.query(PriceDatapoint).filter(PriceDatapoint.event_id == event_id).order_by(PriceDatapoint.observation_timestamp.desc()).first()

    if most_recent is None:
        print("No datapoints found for event.")
        return False
    
    else:
        observation_timestamp = most_recent.observation_timestamp.date()
        print(f"Most recent observation timestamp: {observation_timestamp}")
        today = datetime.datetime.now().date()
        print(f"Today's date: {today}")
        return observation_timestamp == today

def create_price_datapoint(session: Session, event_id: int, section: str, row: str, price: float, source_url: str, section_supply: int) -> None:
    new_datapoint = PriceDatapoint(event_id=event_id, section=section, row=row, price=price, source_url=source_url, section_inventory_count=section_supply)
    print(new_datapoint)
    session.add(new_datapoint)

    if COMMIT_CHANGES:
        session.commit()

def check_for_existing_datapoint_and_add_if_necessary(event_id: int, section: str, row: str, price: float, source_url: str, section_supply: int) -> None:
    db_engine = create_and_return_db_engine()
    
    with Session(db_engine) as session:
        print(f"Checking for existing datapoint for event {event_id} for today...")

        if not price_datapoint_exists_for_today(session, event_id):
            print("No datapoint found for today, adding new datapoint...")

            # Chop price
            price = round(price, 2)
            create_price_datapoint(session, event_id, section, row, price, source_url, section_supply)

        else:
            print("Datapoint already exists for today, skipping...")

def drop_price_table():
    db_engine = create_and_return_db_engine()

    with Session(db_engine) as s:
        s.execute(text("DROP TABLE IF EXISTS prices"))
        s.commit()

    print("'Price' table dropped.")

def create_price_table():
    PriceDatapoint.__table__.create(create_and_return_db_engine())
    print("'Price' table created.")



if __name__ == "__main__":
    #create_price_table()
    print("Doing nothing...")
    print("Done.")
    sys.exit(0)

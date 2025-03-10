


from app import db, Inventory, PriceDatapoint




def add_inventory_to_db(inventory: list[dict]) -> None:
    """TODO: THIS WAS FANCY COPILOT GENERATED CODE, NOT TESTED"""
    for item in inventory:
        new_inventory_item = Inventory(**item)
        db.session.add(new_inventory_item)
    db.session.commit()



def return_current_price_datapoints_for_event(event_id: int) -> list[PriceDatapoint]:
    return PriceDatapoint.query.filter(PriceDatapoint.event_id == event_id).all()

def price_datapoint_exists_for_today(event_id: int) -> bool:
    """Limit datapoints to max one observation per day"""
    return PriceDatapoint.query.filter(PriceDatapoint.event_id == event_id).filter(PriceDatapoint.observation_timestamp == datetime.datetime.today().date()).first() is not None




if __name__ == "__main__":
    pass
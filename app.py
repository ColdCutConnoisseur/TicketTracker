

import os
import datetime
from sqlalchemy import or_, and_


from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_bootstrap import Bootstrap

from config import MY_DB



app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = MY_DB
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
bootstrap = Bootstrap(app)

class Inventory(db.Model):
    __tablename__ = 'inventory'
    event_id = db.Column(db.Integer, primary_key=True)
    event_name = db.Column(db.String(64))
    venue = db.Column(db.String(64))
    event_date = db.Column(db.DateTime)
    event_time = db.Column(db.Time)
    date_purchased = db.Column(db.DateTime)
    qty_purchased = db.Column(db.Numeric)
    total_cost = db.Column(db.Numeric) #decimal.Decimal
    cost_per = db.Column(db.Numeric)
    section = db.Column(db.String(64))
    row = db.Column(db.String(64))
    seat = db.Column(db.String(64))
    sale_payout_date = db.Column(db.DateTime, nullable=True, default=None) #same as is_open --> if no date
    self_use_qty = db.Column(db.Integer, nullable=True)
    sale_total_proceeds = db.Column(db.Numeric, nullable=True)
    sale_marketplace = db.Column(db.String(64), nullable=True)
    notes = db.Column(db.Text, nullable=True)
    manual_price_track = db.Column(db.Float, nullable=True)
    check_price_url = db.Column(db.Text, nullable=True)

    def __repr__(self):
        return '<Inventory %r>' % self.event_name

class PriceDatapoint(db.Model):
    __tablename__ = 'prices'
    observation_id = db.Column(db.Integer, primary_key=True)
    observation_timestamp = db.Column(db.TIMESTAMP, default=datetime.datetime.now)
    event_id = db.Column(db.Integer, db.ForeignKey('inventory.event_id'))
    section = db.Column(db.String(64))
    row = db.Column(db.String(64))
    price = db.Column(db.Numeric)
    source = db.Column(db.String(64), default="TickPick")
    source_url = db.Column(db.Text)
    section_inventory_count = db.Column(db.Integer)

    def __repr__(self):
        return '<PriceDatapoint %r>' % self.price

    """
    def __dict__(self):
        return {'observation_id': self.observation_id, 'observation_timestamp': self.observation_timestamp, 'event_id': self.event_id, 'section': self.section, 'row': self.row, 'price': self.price, 'source': self.source, 'source_url': self.source_url, 'section_inventory_count': self.section_inventory_count}
    """

@app.template_filter('formatEventName')
def _jinja2_filter_event_name(name_text):
    # Replace underscores
    name = name_text.replace("_", " ")
    
    all_words = name.split(" ")

    capped = [word.upper() if word == 'cw' else word.capitalize() for word in all_words]

    capped = " ".join(capped)
    return capped


@app.route('/')
def index():
    closed_inventory = Inventory.query.filter(or_(Inventory.sale_payout_date.is_not(None)), (Inventory.event_date < datetime.datetime.today())).all()  # or event_date > current_date
    closed_headers = ["Event Name", "Total Cost", "Total Proceeds", "Event PnL", "Date Sold"]

    open_inventory = Inventory.query.filter(and_(Inventory.sale_payout_date.is_(None)), ((Inventory.event_date >= datetime.datetime.today().date()))).all()

    # Get info for price and supply charts
    open_event_ids = [event.event_id for event in open_inventory]
    #print(open_event_ids)
    
    # Pull price data for open events
    open_event_dps = PriceDatapoint.query.filter(PriceDatapoint.event_id.in_(open_event_ids)).all()
    #print(open_event_dps)

    # Assert that datapoints are sorted by date
    open_event_dps.sort(key=lambda x: x.observation_timestamp)

    # Try as dict for javascript charting / sorting
    open_event_dps = {dp.observation_id : [dp.event_id, dp.price, dp.observation_timestamp] for dp in open_event_dps}

    open_headers = ["Event Name", "Venue", "Event Date", "Qty Purchased", "Total Cost", "Cost Per", "Section", "Row", "Seat", "Notes", "Price Chart"]
    return render_template('new_index.html',
                           closed_headers=closed_headers,
                           closed_inventory=closed_inventory,
                           open_headers=open_headers,
                           open_inventory=open_inventory,
                           open_event_ids=open_event_ids,
                           open_event_dps=open_event_dps)




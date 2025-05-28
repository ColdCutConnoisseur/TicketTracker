"""Flask app -- Database schema and creation, main dashboard view, and a custom jinja filter"""

import os
import datetime
import calendar
from sqlalchemy import or_, and_


from flask import Flask, render_template, request, jsonify, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_bootstrap import Bootstrap
from flask_wtf import FlaskForm
from wtforms import StringField, DateTimeField, TimeField, DateField, DecimalField, IntegerField, TextAreaField, FloatField
from wtforms.validators import DataRequired, Optional

from config import MY_DB



app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = MY_DB
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = "thisisthekeytoeverythingihopeyoudontseeit"

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
    
    def to_dict(self):
        result = {}
        for c in self.__table__.columns:
            value = getattr(self, c.name)
            if isinstance(value, (datetime.date, datetime.time, datetime.datetime)):
                value = value.isoformat()  # ISO 8601 (safe default)
            result[c.name] = value
        return result

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

class InventoryForm(FlaskForm):
    event_name = StringField('Event Name', validators=[DataRequired()])
    venue = StringField('Venue', validators=[DataRequired()])
    event_date = DateField('Event Date', format="%Y-%m-%d", validators=[DataRequired()]) # DateTimeField   --> '%Y-%m-%d %H:%M'
    event_time = TimeField('Event Time', format='%H:%M', validators=[DataRequired()])
    date_purchased = DateField('Date Purchased', format="%Y-%m-%d", validators=[DataRequired()]) # DateTimeField   --> '%Y-%m-%d %H:%M'
    qty_purchased = DecimalField('Qty Purchased', validators=[DataRequired()])
    total_cost = DecimalField('Total Cost', validators=[DataRequired()])
    cost_per = DecimalField('Cost Per', validators=[DataRequired()])
    section = StringField('Section', validators=[DataRequired()])
    row = StringField('Row', validators=[DataRequired()])
    seat = StringField('Seat', validators=[DataRequired()])
    notes = TextAreaField('Notes', filters=[lambda x: x or None], validators=[Optional()])
    check_price_url = TextAreaField('Check Price URL', filters=[lambda x: x or None], validators=[Optional()])

class DEPRWeekObj:
    def __init__(self, week_number, week_array):
        self.week_number = week_number

        self.sunday = week_array[0]
        self.monday = week_array[1]
        self.tuesday = week_array[2]
        self.wednesday = week_array[3]
        self.thursday = week_array[4]
        self.friday = week_array[5]
        self.saturday = week_array[6]

class CalendarMap:
    def __init__(self, month, year, calendar_month_range):
        self.month = month
        self.year = year
        self.month_starts_on = calendar_month_range[0]
        self.days_in_month = calendar_month_range[1]

        self.mapping = []

        self.create_mapping()

    def create_mapping(self):
        """So hard to read -- maybe don't use a million 'while' loops"""
        week = 1
        current_day_of_week = self.month_starts_on + 1
        weekday_num_generator = (n for n in range(1, self.days_in_month + 1))

        while week <= 5:
            current_week = []

            while current_day_of_week < 7:
                try:
                    current_week.append(next(weekday_num_generator))
                    current_day_of_week += 1

                except StopIteration:
                    if len(current_week) < 7:
                        diff = 7 - len(current_week)

                        blanks = [None] * diff

                        current_week.extend(blanks)
                        self.mapping.append(current_week)
                        return 0

            while len(current_week) < 7:
                current_week.insert(0, None)

            self.mapping.append(current_week)

            week += 1
            current_day_of_week = 0

    def __repr__(self):
        return str(self.mapping)


@app.template_filter('formatEventName')
def _jinja2_filter_event_name(name_text):
    # Replace underscores
    name = name_text.replace("_", " ")
    all_words = name.split(" ")
    capped = [word.upper() if word == 'cw' else word.capitalize() for word in all_words]
    capped = " ".join(capped)
    return capped

@app.template_filter('noNull')
def _jinja2_filter_nones(val):
    r = 0 if val is None else val
    return r

@app.template_filter('dollarFormat')
def _jinja2_format_for_dollar_amount(number):
    if not number:
        return ''
    
    else:
        if number >= 0:
            return f"${number:.2f}"
        
        else:
            return f"-${abs(number):.2f}"
        
@app.template_filter('isCurrentMonthEvent')
def _jinja2_find_upcoming_for_current_cal_date(current_day, current_month_mapping, this_month_inventory):
    today_inventory = [e for e in this_month_inventory if e.event_date.day == current_day]
    return today_inventory

def create_event_last_pricing_supply_mapping(open_event_ids):
    mapping = {}

    for match_id in open_event_ids:
        
        pds = PriceDatapoint.query.filter(PriceDatapoint.event_id==match_id).order_by(
                                 PriceDatapoint.observation_timestamp.desc()).limit(2).all()

        if pds:

            # Observation of length 1 will be newly listed or tracked events
            if len(pds) == 1:
                observation = pds[0]
                price_supply_data = [observation.price, observation.section_inventory_count, True, True]

            elif len(pds) == 2:
                pd_today, pd_yesterday = pds
                price_uptick = pd_today.price > pd_yesterday.price
                supply_uptick = pd_today.section_inventory_count > pd_yesterday.section_inventory_count

                price_supply_data = [pd_today.price, pd_today.section_inventory_count, price_uptick, supply_uptick]

        else:
            price_supply_data = [None, None, None, None]
        
        mapping[match_id] = price_supply_data

    return mapping


def create_and_return_calendar_map(current_year, current_month):
    now_month_range = calendar.monthrange(current_year, current_month)
    calendar_mapping_now = CalendarMap(current_month, current_year, now_month_range)
    return calendar_mapping_now

def fetch_closed_inventory():
    """Return Inventory items where there is a 'payout_date' attribute (early sale) or if the event has already occurred"""
    closed_inventory = Inventory.query.filter(or_(Inventory.sale_payout_date.is_not(None), Inventory.event_date < (datetime.datetime.today()))).all()
    closed_inventory.sort(key=lambda x: x.event_date)
    return closed_inventory

def fetch_open_inventory():
    open_inventory = Inventory.query.filter(and_(Inventory.sale_payout_date.is_(None)), ((Inventory.event_date >= datetime.datetime.today().date()))).all()
    open_inventory.sort(key=lambda x: x.event_date)
    return open_inventory

def calculate_mark_to_market(price_supply_mapping, open_inventory):
    """Instead of doing this in jinja, just do this here"""
    mtm_count = 0

    for inventory_item in open_inventory:
        item_qty = inventory_item.qty_purchased
        pulled_price = price_supply_mapping[inventory_item.event_id][0]
        item_current_price = pulled_price if pulled_price else inventory_item.cost_per
        product = item_qty * item_current_price
        mtm_count += product

    return mtm_count

@app.route('/', methods=['GET', 'POST'])
def index():
    current_year = datetime.datetime.now().year
    current_month = datetime.datetime.now().month
    
    # Run calendar logic for 'watchlist' tab
    calendar_mapping_now = create_and_return_calendar_map(current_year, current_month)

    # Closed Inventory
    closed_headers = ["Event Name", "Total Cost", "Total Proceeds", "Event PnL", "Event Return", "Date Sold"]
    closed_inventory = fetch_closed_inventory()

    # Open Inventory
    open_inventory = fetch_open_inventory()
    this_month_inventory = [i for i in open_inventory if (i.event_date.year == current_year and i.event_date.month == current_month)]

    # Get info for price and supply charts
    open_event_ids = [event.event_id for event in open_inventory]
    
    # Pull price data for open events
    open_event_dps = PriceDatapoint.query.filter(PriceDatapoint.event_id.in_(open_event_ids)).all()

    # Assert that datapoints are sorted by date
    open_event_dps.sort(key=lambda x: x.observation_timestamp)

    # Try as dict for javascript charting / sorting
    open_event_dps = {dp.observation_id : [dp.event_id, dp.price, dp.observation_timestamp, dp.section_inventory_count] for dp in open_event_dps}

    # Get Last Price & Supply Observations
    price_supply_mapping = create_event_last_pricing_supply_mapping(open_event_ids)

    # MTM Calculation
    mtm_count = calculate_mark_to_market(price_supply_mapping, open_inventory)

    open_headers = ["Event Name", "Venue", "Event Date", "Qty Purchased", "Total Cost", "Cost Per", "Section", "Row", "Seat", "Notes", "Last Px", "Supply", "Price Chart", "Supply Chart"]
    
    add_form = InventoryForm()

    # DEBUG
    if request.method == "POST":
        print("Raw POST data:", request.form)

    if add_form.validate_on_submit():
        inv = Inventory(
            event_name=add_form.event_name.data,
            venue=add_form.venue.data,
            event_date=add_form.event_date.data,
            event_time=add_form.event_time.data,
            date_purchased=add_form.date_purchased.data,
            qty_purchased=add_form.qty_purchased.data,
            total_cost=add_form.total_cost.data,
            cost_per=add_form.cost_per.data,
            section=add_form.section.data,
            row=add_form.row.data,
            seat=add_form.seat.data,
            notes=add_form.notes.data,
            check_price_url=add_form.check_price_url.data
        )
        db.session.add(inv)
        db.session.commit()
        flash('Inventory item added successfully!', 'success')
        return redirect(url_for('successful_add'))

    return render_template('new_index.html',
                           closed_headers=closed_headers,
                           closed_inventory=closed_inventory,
                           open_headers=open_headers,
                           open_inventory=open_inventory,
                           open_event_ids=open_event_ids,
                           open_event_dps=open_event_dps,
                           price_supply_mapping=price_supply_mapping,
                           calendar_mapping_now=calendar_mapping_now,
                           this_month_inventory=this_month_inventory,
                           mtm_count=mtm_count,
                           add_form=add_form)

@app.route('/success_message')
def successful_add():
    return "<h3>Inventory Added Successfully!</h3>"

@app.route('/search_inventory')
def search_inventory():
    q = request.args.get('q', '').strip()

    if not q:
        print("No query string!")
        return jsonify({})
    
    if q:
        suggested = Inventory.query.filter(Inventory.event_name.like(f"%{q}%")).limit(10).all()
        return jsonify([item.to_dict() for item in suggested])
    







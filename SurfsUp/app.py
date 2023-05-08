# Import the dependencies.
import numpy as np
import datetime as dt
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify

#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()

# reflect the tables
Base.prepare(autoload_with=engine)

# Save references to each table
Measurement = Base.classes.measurement
Station = Base.classes.station

# Create our session (link) from Python to the DB
session = Session(engine)

# Get the maximum date and then find out one year less than max_date
max_date = session.query(func.max(Measurement.date)).first()
max_date1 = max_date[0].split("-")
year = int(max_date1[0])
month = int(max_date1[1])
day = int(max_date1[2])
max_date_less_year = dt.date(year, month, day) - dt.timedelta(days=365)

# Get the active stations
active_stations = session.query(Measurement.station, func.count(Measurement.station)).\
                    group_by(Measurement.station).\
                    order_by(func.count(Measurement.station).desc()).all()

# Get the most active station
most_active_station = active_stations[0][0]

session.close()

#################################################
# Flask Setup
#################################################
app = Flask(__name__)

#################################################
# Flask Routes
#################################################
@app.route('/')
def welcome():
    """List all available api routes."""
    return (
        f"Available Routes:<br/>"
        f"<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/start<br/>"
        f"/api/v1.0/start/end<br/>"
    )

@app.route('/api/v1.0/precipitation')
def prec():
    """Precipitation Route"""
    """SELECT date, prcp FROM measurement WHERE date >= max_date_last_year"""
    # Create our session (link) from Python to the DB
    session = Session(engine)

    results = session.query(Measurement.date, Measurement.prcp).\
                filter(Measurement.date >= max_date_less_year).all()

    # Close session
    session.close()

    # Convert into list of dictionary
    all_prcp = []
    for date, prcp in results:
        prcp_dict = {}
        prcp_dict[date] = prcp
        all_prcp.append(prcp_dict)

    return jsonify(all_prcp)

@app.route('/api/v1.0/stations')
def stations():
    """Stations Route"""
    """SELECT station FROM stations ORDER BY stations"""
    # Create our session (link) from Python to the DB
    session = Session(engine)
    results = session.query(Station.station).order_by(Station.station).all()

    # Close session
    session.close()

    # Convert list of tuples into normal list
    stations = list(np.ravel(results))

    return jsonify(stations)

@app.route('/api/v1.0/tobs')
def tobs():
    """TOBs Route"""
    """SELECT date, tobs FROM measurement 
       WHERE date >= max_date_last_year
       AND station = most_active_station
    """

    # Create our session (link) from Python to the DB
    session = Session(engine)
    results = session.query(Measurement.date, Measurement.tobs).\
                    filter(Measurement.date >= max_date_less_year).\
                    filter(Measurement.station==most_active_station).all()

    # Close session
    session.close()

    all_tobs = []
    for date, tobs in results:
        tobs_list = []
        tobs_list.append(date)
        tobs_list.append(tobs)
        all_tobs.append(tobs_list)

    return jsonify(all_tobs)

@app.route('/api/v1.0/start')
def start():
    """Start Route"""
    return (
        f"Start"
    )

@app.route('/api/v1.0/start/end')
def start_end():
    """Start and End Route"""
    return (
        f"Start and End"
    )

if __name__ == '__main__':
    app.run(debug=True)
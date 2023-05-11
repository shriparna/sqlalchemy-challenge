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

# Close the session
session.close()

# Generic function to get the min, max and avg of temperature for a given start or start and end dates
def get_tob_values(start_date, end_date):
    # Create our session (link) from Python to the DB
    session = Session(engine)

    # Get the details from the measurement table
    tobs_result = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
                filter(Measurement.date >= start_date).\
                filter(Measurement.date <= end_date).all()

    # Close the session
    session.close()

    # Add details in the list of dictionary
    tobs_dictionary_list = []
    tobs_dict = {
        "TMIN" : tobs_result[0][0],
        "TAVG" : tobs_result[0][1], 
        "TMAX" : tobs_result[0][2]
    }
    tobs_dictionary_list.append(tobs_dict) 

    print(tobs_dictionary_list)
    
    return(tobs_dictionary_list)

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
        f"<h1>Available Routes:</h1><br/>"
        f"<ol>"
        f"<li>/api/v1.0/precipitation</li>Gives the list of JSON directories with date as key and precipitation as value<br/><br/>"
        f"<li>/api/v1.0/stations</li>Gives the JSON list of stations<br/><br/>"
        f"<li>/api/v1.0/tobs</li>Gives the JSON list of dictionaries with date as key and temperature observed as value<br/><br/>"
        f"<li>/api/v1.0/<em>start</em></li>Gives the JSON list of a dictionary with key as TAVG for average temperature observed, "
        f"TMAX for maxmium temprature observed and TMIN for minumum temperature observed from a give start date<br/>"
        f"Usage: Replace <em>start</em> with date, e.g. /api/v1.0/2016-01-01 will give the above details from this date onwards<br/></br>"
        f"<li>/api/v1.0/<em>start</em>/<em>end</em></li>Gives the JSON list of a dictionary with key as TAVG for average temperature observed, "
        f"TMAX as maxmium temprature observed and TMIN for minumum temperature observed between the given start and end date range<br/>"
        f"Usage: Replace <em>start</em> and <em>end</em> with date, e.g. /api/v1.0/2016-01-01/2016-12-31 will give the above details between these dates"
        f"</ol>"
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

    # Convert into dictionary
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
    """
       SELECT date, tobs FROM measurement 
       WHERE date >= max_date_last_year
       AND station = most_active_station
    """

    # Create our session (link) from Python to the DB
    session = Session(engine)
    results = session.query(Measurement.date, Measurement.tobs).\
                    filter(Measurement.date >= max_date_less_year).\
                    filter(Measurement.station == most_active_station).all()

    # Close session
    session.close()

    all_tobs = []
    for date, tobs in results:
        tobs_dict = {}
        tobs_dict[date] = tobs
        all_tobs.append(tobs_dict)
    return jsonify(all_tobs)

@app.route('/api/v1.0/<start>')
def get_start_tobs(start):
    """Start Route"""
    """
       SELECT MIN(tobs), AVG(tobs), MAX(tobs)
       FROM   measurement
       WHERE  date >= <start_date>
    """

    # We can put end as the current date
    # So that we can reuse the same function
    end = dt.datetime.today().strftime("%Y-%m/%d")
    return (jsonify(get_tob_values(start, end)))

@app.route('/api/v1.0/<start>/<end>')
def get_start_end_tobs(start, end):
    """Start and End Route"""
    """
       SELECT MIN(tobs), AVG(tobs), MAX(tobs)
       FROM   measurement
       WHERE  date BETWEEN <start_date> AND <end_date>
    """

    return (jsonify(get_tob_values(start, end)))

if __name__ == '__main__':
    app.run(debug=True)
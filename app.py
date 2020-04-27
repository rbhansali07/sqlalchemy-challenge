import numpy as np

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
import datetime as dt
from flask import Flask, jsonify


#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)

# Save reference to the table
Station = Base.classes.station
Measurement = Base.classes.measurement

#################################################
# Flask Setup
#################################################
app = Flask(__name__)


#################################################
# Flask Routes
#################################################

@app.route("/")
def Home():
    """List all available api routes."""
    return (
        f"Available Routes:<br/><br/>"
        f"-Date and Precipitation information <br/>"
        f"/api/v1.0/precipitation<br/><br/>"
        f"-Station information<br/>"
        f"/api/v1.0/stations<br/><br/>"
        f"Temperature Observation for previous year for most active station<br/>"
        f"/api/v1.0/tobs<br/><br/>"
        f"-min, average, max temperature for a starting date e.g. /api/v1.0/2016-01-01<br/>"
        f"/api/v1.0/start_date<br/><br/>"
        f"-min, average, max temperature for a date range e.g. /api/v1.0/2016-01-01/2016-07-21<br/>"
        f"/api/v1.0/start_date/end_date"
    )


@app.route("/api/v1.0/precipitation")
def precip():
    # Create our session (link) from Python to the DB
    session = Session(engine)
    #query to find most recent date
    first_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first()
    
    # Calculate the date 1 year ago from the last data point in the database
    date_last_year = dt.date(2017, 8, 23) - dt.timedelta(days=365)
    
    # Perform a query to retrieve the data and precipitation scores
    prcp_data = session.query(Measurement.date, Measurement.prcp).filter(Measurement.date >= date_last_year).all()
    session.close()
    
    all_prcp = []
    for date, prcp in prcp_data:
        prcp_dict = {}
        prcp_dict["date"] = date
        prcp_dict["prcp"] = prcp
        all_prcp.append(prcp_dict)
    
    return jsonify(all_prcp)


@app.route("/api/v1.0/stations")
def stations():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    """Return list of stations"""
    # Query all stations
    station_data = session.query(Station.station, Station.name).all()

    session.close()

    # Create a station dictionary
    all_station = []
    for station, name in station_data:
        station_dict = {}
        station_dict["station"] = station
        station_dict["name"] = name
        all_station.append(station_dict)

    return jsonify(all_station)

@app.route("/api/v1.0/tobs")
def temp_obs():
    # Create our session (link) from Python to the DB
    session = Session(engine)
    
    # find active station
    active_station = session.query(Measurement.station, func.count(Measurement.station)).\
    group_by(Measurement.station).\
    order_by(func.count(Measurement.station).desc()).all()

    """Return list of tempersture for previous year (2016)"""
    # Query active station for temp data
    temp_data = session.query(Station.name, Measurement.tobs, Measurement.date).\
                filter(Measurement.date >= '2016-01-01').filter(Measurement.date <= '2016-12-31').\
                filter(Measurement.station == active_station[0][0]).all()

    session.close()

    # Create a station dictionary
    all_temp = []
    for name, tobs, date in temp_data:
        temp_dict = {}
        temp_dict["Station Name"] = name
        temp_dict["Temp observation"] = tobs
        temp_dict["Date"] = date
        all_temp.append(temp_dict)

    return jsonify(all_temp)

@app.route("/api/v1.0/<start>")
def start(start=None):
    # Create our session (link) from Python to the DB
    session = Session(engine)
   

    """Return tmin, tavg, tmax for starting date"""
    # Query active station for temp data
    start_date_data = session.query(Measurement.date, func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
                       filter(Measurement.date >= start).group_by(Measurement.date).all()

    session.close()
    
    return jsonify(list(start_date_data))

@app.route("/api/v1.0/<start>/<end>")
def start_end(start=None, end=None):
    # Create our session (link) from Python to the DB
    session = Session(engine)
   
    """Return tmin, tavg, tmax for a date range"""
    # Query active station for temp data
    date_range_data = session.query(Measurement.date, func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
                       filter(Measurement.date >= start).filter(Measurement.date <= end).group_by(Measurement.date).all()

    session.close()
    
    return jsonify(list(date_range_data))


if __name__ == '__main__':
    app.run(debug=True)

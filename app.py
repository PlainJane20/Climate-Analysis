# Dependencies
import numpy as np
import datetime as dt
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify

# Create engine using the `hawaii.sqlite` database file
engine = create_engine("sqlite:///Resources/hawaii.sqlite")
# conn = engine.connect()

# Reflect an existing database and tables
Base = automap_base()
Base.prepare(engine, reflect=True)

# Save reference to the tables
Measurement = Base.classes.measurement
Station = Base.classes.station

session = Session(engine)

# Find the last date in the database
last_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first()
# print(last_date)

# Calculate the date 1 year ago from the last data point in the database
query_date = dt.date(2017,8,23) - dt.timedelta(days=365)

session.close()

# Create Flask app
app = Flask(__name__)

# Flask Routes
# Define what to do when user hits the index route
@app.route("/")
def home():
    """List all available api routes."""
    return(
        f"Welcome to Hawaii Climate Page<br/> "
        f"Available Routes:<br/>"
        f"<br/>"  
        f"The list of precipitation data with dates:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"<br/>"
        f"The list of stations and names:<br/>"
        f"/api/v1.0/stations<br/>"
        f"<br/>"
        f"Find the list of temprture observations last data point:<br/>"
        f"/api/v1.0/tobs<br/>"
        f"<br/>"
        f"Min, Max. and Avg. temperatures for given start date: (please use 'yyyy-mm-dd' format):<br/>"
        f"/api/v1.0/min_max_avg/&lt;start date&gt;<br/>"
        f"<br/>"
        f"Min. Max. and Avg. tempratures for given start and end date: (please use 'yyyy-mm-dd'/'yyyy-mm-dd' format for start and end values):<br/>"
        f"/api/v1.0/min_max_avg/&lt;start date&gt;/&lt;end date&gt;<br/>"
        f"<br/>"
        f"i.e. <a href='/api/v1.0/min_max_avg/2010-01-01/2017-12-31' target='_blank'>/api/v1.0/min_max_avg/2010-01-01/2017-12-31</a>"
    )

# Precipitation route
@app.route("/api/v1.0/precipitation")
def precipitation():
    # Create the session link
    session = Session(engine)

   # Query precipitation and date values 
    results = session.query(Measurement.date, Measurement.prcp).all()
        
    session.close()
    
    # Create a dictionary as date the key and prcp as the value
    precipitation = []
    for result in results:
        r = {}
        r[result[0]] = result[1]
        precipitation.append(r)

    return jsonify(precipitation )

# Create stations route    
@app.route("/api/v1.0/stations")
def stations():
    # Create the session link
    session = Session(engine)
    
    # Query data to get stations list
    results = session.query(Station.station, Station.name).all()
    
    session.close()

    # Convert list of tuples into list of dictionaries for each station and name
    station_list = []
    for result in results:
        r = {}
        r["station"]= result[0]
        r["name"] = result[1]
        station_list.append(r)
    
    # jsonify the list
    return jsonify(station_list)

# Create temperatures route
@app.route("/api/v1.0/tobs")
def tobs():
    # Create session link
    session = Session(engine)
    
    # Query tempratures from a year from the last data point. 
    # query_date  is "2017-08-23" for the last year query
    results = session.query(Measurement.tobs, Measurement.date).filter(Measurement.date >= query_date).all()

    session.close()

    # convert list of tuples to show date and temprature values
    tobs_list = []
    for result in results:
        r = {}
        r["date"] = result[1]
        r["temprature"] = result[0]
        tobs_list.append(r)

    # jsonify the list
    return jsonify(tobs_list)

# create start route
@app.route("/api/v1.0/min_max_avg/<start>")
def start(start):
    # create session link
    session = Session(engine)

    # Take any date and convert to yyyy-mm-dd format for the query
    start_dt = dt.datetime.strptime(start, '%Y-%m-%d')

    # Query data for the start date value
    results = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).filter(Measurement.date >= start_dt).all()

    session.close()

    # Create a list to hold results
    t_list = []
    for result in results:
        r = {}
        r["StartDate"] = start_dt
        r["TMIN"] = result[0]
        r["TAVG"] = result[1]
        r["TMAX"] = result[2]
        t_list.append(r)

    # jsonify the result
    return jsonify(t_list)

@app.route("/api/v1.0/min_max_avg/<start>/<end>")
def start_end(start, end):
    # Create session link
    session = Session(engine)

    # Take start and end dates and convert to yyyy-mm-dd format for the query
    start_dt = dt.datetime.strptime(start, '%Y-%m-%d')
    end_dt = dt.datetime.strptime(end, "%Y-%m-%d")

    # Query data for the start date value
    results = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).filter(Measurement.date >= start_dt).filter(Measurement.date <= end_dt)

    session.close()

    # Create a list to hold results
    t_list = []
    for result in results:
        r = {}
        r["StartDate"] = start_dt
        r["EndDate"] = end_dt
        r["TMIN"] = result[0]
        r["TAVG"] = result[1]
        r["TMAX"] = result[2]
        t_list.append(r)

    # jsonify the result
    return jsonify(t_list)

#run the app
if __name__ == "__main__":
    app.run(debug=True)
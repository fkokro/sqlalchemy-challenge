#Step 2 - Create a Climate App




#################################################
#Import Relevant Libraries
#################################################

import numpy as np
import pandas as pd

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
from sqlalchemy import create_engine, inspect

from flask import Flask, jsonify
import datetime as dt

#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)

# Create the inspector and connect it to the engine
inspector = inspect(engine)
#Check connection
#print(inspector.get_table_names())

#################################################
# Flask Setup
#################################################
app = Flask(__name__)

#################################################
# Flask Routes
#################################################
@app.route("/")
def welcome():
    """List all available api routes."""
    return (
        f"Available Routes:<br/>"
        f"<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"- List of prior year rain totals from all stations<br/>"
        f"<br/>"
        f"/api/v1.0/stations<br/>"
        f"- List of Station numbers and names<br/>"
        f"<br/>"
        f"/api/v1.0/tobs<br/>"
        f"- List of prior year temperatures from all stations<br/>"
        f"<br/>"
        f"/api/v1.0/start<br/>"
        f"- When given the start date (YYYY-MM-DD), calculates the MIN/AVG/MAX temperature for all dates greater than and equal to the start date<br/>"
        f"<br/>"
        f"/api/v1.0/start/end<br/>"
        f"- When given the start and the end date (YYYY-MM-DD), calculate the MIN/AVG/MAX temperature for dates between the start and end date inclusive<br/>"

    )
##########################################
@app.route("/api/v1.0/precipitation")
def precipitation():
    """Return a list of rain fall for prior year"""

    # Design a query to retrieve the last 12 months of precipitation data 
#           * Convert the query results to a Dictionary using `date` as the key and `prcp` as the value.
#           * Return the json representation of your dictionary.
    results = engine.execute("select date, prcp from measurement where date >= '2016-08-23' ").fetchall()
    date_results = [result[0] for result in results]
    prcp_results = [result[1] for result in results]
    # Save the query results as a Pandas DataFrame and set the index to the date column
    # Sort the dataframe by date
    df = pd.DataFrame({'Date' : date_results, 'Precipitation': prcp_results}).sort_values(by=['Date'], ascending=False)
    #Convert Dataframe to dictionary
    rain_totals = df.to_dict("list")
    return jsonify (rain_totals)
##########################################
@app.route("/api/v1.0/stations")
def stations():
    """Return a JSON list of stations from the dataset."""

    #Query list of stations from database.
    stations = engine.execute("SELECT DISTINCT station FROM measurement").fetchall()
    station_list = [result1[0] for result1 in stations]

    return jsonify (station_list)
##########################################
@app.route("/api/v1.0/tobs")
def tobs():
    """query for the dates and temperature observations from a year from the last data point."""
    """Return a JSON list of Temperature Observations (tobs) for the previous year."""
    prep_results = engine.execute("select date, tobs from measurement where date between '2016-08-23' and '2017-8-23' and station = 'USC00519281'").fetchall()
    df1 = pd.DataFrame({'Date': [result[0] for result in prep_results], 'tobs':[result[1] for result in prep_results]}).sort_values(by=['Date'], ascending=False)
    tobs_totals = df1.to_dict("list")
    return jsonify (tobs_totals)
 #################################################
# Database Setup
#################################################

# Save reference to the table
Measurement = Base.classes.measurement
Station = Base.classes.station
# Create our session (link) from Python to the DB
session = Session(engine)   
#########################################################################################
@app.route("/api/v1.0/<start>")
def trip1(start):

 # go back one year from start date and go to end of data for Min/Avg/Max temp   
    start_date= dt.datetime.strptime(start, '%Y-%m-%d')
    last_year = dt.timedelta(days=365)
    start = start_date-last_year
    end =  dt.date(2017, 8, 23)
    trip_data = session.query(func.min(Measurements.tobs), func.avg(Measurements.tobs), func.max(Measurements.tobs)).\
        filter(Measurements.date >= start).filter(Measurements.date <= end).all()
    trip = list(np.ravel(trip_data))
    return jsonify(trip)

#########################################################################################
@app.route("/api/v1.0/<start>/<end>")
def trip2(start,end):

  # go back one year from start/end date and get Min/Avg/Max temp     
    start_date= dt.datetime.strptime(start, '%Y-%m-%d')
    end_date= dt.datetime.strptime(end,'%Y-%m-%d')
    last_year = dt.timedelta(days=365)
    start = start_date-last_year
    end = end_date-last_year
    trip_data = session.query(func.min(Measurements.tobs), func.avg(Measurements.tobs), func.max(Measurements.tobs)).\
        filter(Measurements.date >= start).filter(Measurements.date <= end).all()
    trip = list(np.ravel(trip_data))
    return jsonify(trip)

#########################################################################################

if __name__ == "__main__":
    app.run(debug=True)


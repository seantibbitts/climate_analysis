import numpy as np
import pandas as pd

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

import datetime as dt

from flask import Flask, jsonify

# Create a database connection
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)

# Save references to each table
Measurement = Base.classes.measurement
Station = Base.classes.station

# Create Flask instance
app = Flask(__name__)

# Create webpage routes
@app.route("/")
def index():
    """List all available api routes."""
    return (
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/daterange/&lt;start&gt; and /api/v1.0/daterange/&lt;start&gt;/&lt;end&gt;<br/>"
        "(for dates between 2010-01-01 and 2017-08-23)"
    )

@app.route("/api/v1.0/precipitation")
def precip():
    # Create our session (link) from Python to the DB
    session = Session(engine)
    # Design a query to retrieve the last 12 months of precipitation data
    max_date = session.query(func.max(Measurement.date)).all()[0][0]
    # Calculate the date 1 year ago from the last data point in the database
    max_datetime = dt.datetime.strptime(max_date, '%Y-%m-%d').date()
    prev_year_date = dt.date(max_datetime.year - 1, max_datetime.month, max_datetime.day)
    # Perform a query to retrieve the data and precipitation scores
    # Retrieved average precipitation across all weather stations
    last_12_prcp = session.query(Measurement.date, func.avg(Measurement.prcp))\
        .filter(Measurement.date > prev_year_date)\
            .group_by(Measurement.date).all()
    # Save the query results as a Pandas DataFrame and set the index to the date column
    last_12_prcp_df = pd.DataFrame(last_12_prcp, columns = ['Date','Precipitation']).set_index('Date')
    # Sort the dataframe by date
    last_12_prcp_df_sorted = last_12_prcp_df.sort_index()
    # Convert to dictionary with dates as keys
    last_12_dict = last_12_prcp_df_sorted.to_dict()
    # Close session
    session.close()
    return jsonify(last_12_dict)

@app.route("/api/v1.0/stations")
def stations():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    # Get all stations
    stations = list(np.ravel(session.query(Station.station).all()))

    # Close session
    session.close()
    return jsonify(stations)

@app.route("/api/v1.0/tobs")
def temps():
    # Create our session (link) from Python to the DB
    session = Session(engine)
    # Design a query to retrieve the last 12 months of temperature data
    max_date = session.query(func.max(Measurement.date)).all()[0][0]
    # Calculate the date 1 year ago from the last data point in the database
    max_datetime = dt.datetime.strptime(max_date, '%Y-%m-%d').date()
    prev_year_date = dt.date(max_datetime.year - 1, max_datetime.month, max_datetime.day)
    # Perform a query to retrieve the temperature scores
    last_12_temp = list(np.ravel(session.query(Measurement.tobs)\
        .filter(Measurement.date > prev_year_date).all()))
    # Close session
    session.close()
    return jsonify(last_12_temp)

@app.route("/api/v1.0/daterange/<start>")
def data_start(start):
    # Create our session (link) from Python to the DB
    session = Session(engine)

    # Query min, avg and max temps for dates after start
    temp_list = list(np.ravel(session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs),
    func.max(Measurement.tobs)).filter(Measurement.date > start).all()))

    # Close session
    session.close()
    return jsonify(temp_list)

@app.route("/api/v1.0/daterange/<start>/<end>")
def date_start_end(start, end):
    # Create our session (link) from Python to the DB
    session = Session(engine)

    # Query min, avg and max temps for dates between start and end
    temp_list = list(np.ravel(session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs),
    func.max(Measurement.tobs)).filter(Measurement.date > start).filter(Measurement.date < end).all()))

    # Close session
    session.close()
    return jsonify(temp_list)

if __name__ == "__main__":
    app.run(debug=True)
#################################################
# James Dietz, SQL Alchemcy / Flask HW 10 (aka 8)
#################################################

import numpy as np

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify

# Added by DL
from sqlalchemy.orm import scoped_session, sessionmaker

#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite")


# Added by DL
db_session = scoped_session(sessionmaker(autocommit=False,
                                         autoflush=False,
                                         bind=engine))

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)

# Save reference to the table

Measurement = Base.classes.measurement
Station = Base.classes.station

#################################################
# Flask Setup
#################################################
app = Flask(__name__)


#################################################
# Flask Routes
#################################################


# Route for Precipitation Query

@app.route("/api/v1.0/precipitation")
def precip_query(): 
    
   precipqry = db_session.query(Measurement.date, Measurement.prcp).filter(Measurement.date <= '2017-08-23').\
    filter(Measurement.date >= '2016-08-24').order_by(Measurement.date).all()
   
   precip_dict = dict(precipqry)   
    
   return jsonify(precip_dict)


# Route for Station List Query

@app.route("/api/v1.0/stations")
def stations_query():
    stations = db_session.query(Measurement.station).group_by(Measurement.station).all()


    return jsonify(stations)


# Route for Temperature Query

@app.route("/api/v1.0/tobs")
def tobs_query():
    
    tobsqry = db_session.query(Measurement.date, Measurement.tobs).filter(Measurement.date <= '2017-08-23').\
        filter(Measurement.date >= '2016-08-24').filter(Measurement.station == 'USC00519281').order_by(Measurement.date).all()

    return jsonify(tobsqry)
    

# Route for Start Date Query

@app.route("/api/v1.0/<start>")
def start_query(start):   
    
    tobstart_query = db_session.query(Measurement.date, func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
        filter(Measurement.date >= start).group_by(Measurement.date).\
        order_by(Measurement.date).all()

    start_list = []
    for date, mintobs, avgtobs, maxtobs in tobstart_query:
        start_dict = {}
        start_dict["*date"] = date
        start_dict["minimum_temperature"] = mintobs
        start_dict["average_temperature"] = avgtobs
        start_dict["maximum_temperature"] = maxtobs
        start_list.append(start_dict)
    return jsonify(start_list)


# Route for Start-End Date Query
@app.route("/api/v1.0/<start>/<end>")
def startend_query(start, end):
    
    tobstart_end_query = db_session.query(Measurement.date, func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
        filter(Measurement.date >= start).filter(Measurement.date <= end).group_by(Measurement.date).\
        order_by(Measurement.date).all()

    start_end_list = []
    for date, mintobs, avgtobs, maxtobs in tobstart_end_query:
        start_end_dict = {}
        start_end_dict["*date"] = date
        start_end_dict["minimum_temperature"] = mintobs
        start_end_dict["average_temperature"] = avgtobs
        start_end_dict["maximum_temperature"] = maxtobs
        start_end_list.append(start_end_dict)
    return jsonify(start_end_list)


# Route for index

@app.route("/")
def welcome():
    return (
        f"Welcome to Hawaii Weather API!<br/>"
        f"-----------------------------<br/>"
        f"Available Routes:<br/>"
        f"  <br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/<start>YYYY-MM-DD<br/>"
        f"/api/v1.0/<start>YYYY-MM-DD/<end>YYYY-MM-DD"
    )

# DL added this tear down code.

@app.teardown_appcontext
def cleanup(resp_or_exc):
    print('Teardown received')
    db_session.remove()

if __name__ == "__main__":
    app.run(debug=True)

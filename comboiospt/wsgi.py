import logging
import bottle
from bottle import get, post, request, response, route, run, app, error, static_file, template
import os
import cgi
from CP import CP
from Refer import Refer

logging.basicConfig(level=logging.DEBUG)
logging.info('Started')

cp = CP()
refer = Refer()

application = bottle.default_app()

@route("/cp/schedules")
def cp_schedules():
    r = cp.schedules(origin=request.query.origin, destination=request.query.destination, date=request.query.date, hour=request.query.hour)
    response.status = r["status"]
    return r;

@route("/cp/details")
def cp_details():
    r = cp.details(requestID=request.query.requestid, index=request.query.i)
    logging.info('details:'+str(r))
    response.status = r["status"]
    return r

@route("/refer/departures")
def refer_departures():
    r = refer.departures(stationId=request.query.stationid)
    response.status = r["status"]
    return r;


@route("/stations.csv")
def stations():
    return static_file("stations.csv",root=".")

@route("/")
def hello():
    return static_file("README.html", root=".")

@error(404)
def fourohfour(error):
    return template("404.html")
    
if __name__ == "__main__":
    run(host='localhost', port=8080, debug=True, reloader=True)

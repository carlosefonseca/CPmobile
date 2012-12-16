import logging
import bottle
from bottle import get, post, request, route, run, app
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
	return cp.schedules(origin=request.query.origin, destination=request.query.destination, date=request.query.date, hour=request.query.hour)

@route("/cp/details")
def cp_details():
	res = cp.details(requestID=request.query.requestid, index=request.query.i)
	logging.info('details:'+str(res))
	return res

@route("/refer/departures")
def refer_departures():
	return refer.departures(stationId=request.query.stationid)


#run(host='localhost', port=8080, debug=True, reloader=True)
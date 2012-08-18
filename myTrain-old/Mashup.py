from CP import CP
from Refer import Refer
import json
import re

class Mashup():

	cp = 0;
	refer = 0;

	def __init__(self, _cp, _refer):
		self.cp = _cp
		self.refer = _refer

	def SchedulesAndStatus(self, origin, destination, date="", hour="", oid):
		cpr = cp.schedules(origin, destination, date, hour)
		referr = refer.Departures(oid)

		

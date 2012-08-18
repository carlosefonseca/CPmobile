import cgi, random, sys
import urlparse
from datetime import datetime
import requests
import re
import json
import sqlite3

from bs4 import BeautifulSoup

class Refer():
	"""Handles parsing of http://refer.pt pages"""

	def departures(self, stationId):
		""" Returns a list of trains that are about to leave the specified station """

		r = requests.get("http://www.refer.pt/MenuPrincipal/Passageiros/PartidaseChegadas.aspx?stationid="+str(stationId)+"&Type=Arrivals")

		soup = BeautifulSoup(r.text)
		leTable = soup.find_all("div", {"class":"mod-table-values"})[0].table
		
		rows = leTable.find_all("tr")
		rows.pop(0) # headers

		results = []

		for r in rows:
			c = r.find_all("td")
			
			result = {}

			result["hour"] = c[0].getText()
			(result["type"], result["trainid"]) = c[1].getText().strip().split("\n")

			result["origin"] = re.findall("stationid=(\d+)\" title=\"([^\"]*)", str(c[2]))[0]
			result["destination"] = re.findall("stationid=(\d+)\" title=\"([^\"]*)", str(c[3]))[0]

			result["status"] = c[5].getText()

			results.append(result)

		return results


	def handle(self, action, args, output = "jsonf"):
		"""Handles commands from the webserver, runs the appropriate method and returns the data in the specified format

		Arguments:
		action	-- the name of the method (available: departures)
		args	-- a dictionary of parameters as created by BaseHTTPServer
		output	-- the format for the output data; the default is jsonf for indented json, anything else returns unindented json
		"""
		result = None
		if action == "departures":
			try:
				result = self.departures(args["stationid"][0])
			except:
				result = self.e("Parameter 'stationid' is required.")

		else:
			result = self.e("Invalid or unspecified action")


		if (result != None):
			if (output == "jsonf"):
				print json.dumps(result, indent=2)
			else:
				print json.dumps(result)


	def e(self, txt):
		"""Generates an error object with the specified message"""
		return {"error":txt}

r = Refer()
# res = r.departures(9431039)
# print res
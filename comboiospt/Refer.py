# -*- coding: utf-8 -*-
import cgi, random, sys
import urlparse
from datetime import datetime
import requests
import re
import json

from bs4 import BeautifulSoup

class Refer():
	"""Handles parsing of http://refer.pt pages"""

	methods_allowed = ('GET',)

	def departures(self, stationId):
		""" Returns a list of trains that are about to leave the specified station """

		r = requests.get("http://www.refer.pt/MenuPrincipal/Passageiros/PartidaseChegadas.aspx?stationid="+str(stationId)+"&Type=Departures")

		soup = BeautifulSoup(r.text)
		msg = soup.find_all("div", {"id":"dnn_ctr569_TrainArrivalsAndDepartures_pnlMessage"})
		if len(msg) > 0:
			if u"Não encontrados resultados" in msg[0].string:
				return {"status":"200 OK", "request": {"station":stationId}, "results":[]}
			else:
				return {"status":"500 Error - please inform developer - ".msg[0], "request": {"station":stationId}, "results":[]}
		leTable = soup.find_all("div", {"class":"mod-table-values"})[0].table
		
		rows = leTable.find_all("tr")
		rows.pop(0) # headers

		results = []

		for r in rows:
			c = r.find_all("td")
			
			result = {}

			result["hour"] = c[0].getText()
			(result["type"], result["train"]) = c[1].getText().strip().split("\n")

			result["origin"] = re.findall("stationid=(\d+)\" title=\"([^\"]*)", str(c[2]))[0]
			result["destination"] = re.findall("stationid=(\d+)\" title=\"([^\"]*)", str(c[3]))[0]

			result["status"] = c[5].getText()

			results.append(result)

		return {"request": {"station":stationId}, "results":results}


	def read(self, request, action):
		"""Handles commands from the webserver, runs the appropriate method and returns the data in the specified format

		Arguments:
		action	-- the name of the method (available: departures)
		args	-- a dictionary of parameters as created by BaseHTTPServer
		output	-- the format for the output data; the default is jsonf for indented json, anything else returns unindented json
		"""
		result = None

		args = request.GET
		output = args["output"] if "output" in args else "jsonf"

		if action == "departures":
			if ("stationid" in args):
				result = self.departures(args["stationid"])
			else:
				result = self.e("Parameter 'stationid' is required.")

		else:
			result = self.e("Invalid or unspecified action. Valid actions for Refer are: 'departures'.")


		if (result != None):
			return result;
			# if (output == "jsonf"):
			# 	print json.dumps(result, indent=2)
			# else:
			# 	print json.dumps(result)


	def e(self, txt):
		"""Generates an error object with the specified message"""
		resp = rc.BAD_REQUEST
		resp.content = {"error":txt}
		return resp

if __name__ == "__main__":
	r = Refer()
	res = r.departures(9431278)
	print json.dumps(res, indent=2)

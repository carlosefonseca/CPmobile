import cgi, random, sys
import urlparse
from datetime import datetime
import requests
import re
import json
import sqlite3

from bs4 import BeautifulSoup

class Refer():
	def Departures(self, stationId):
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

		return json.dumps(results)


# r = Refer()
# res = r.Departures(9431039)
# print res
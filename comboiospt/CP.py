# -*- coding: utf-8 -*-
import logging
import cgi, random, sys
import urlparse
from datetime import datetime
import requests
import re
import json
#import sqlite3

from bs4 import BeautifulSoup

class CP():
    cookies = []
    headers = {'User-Agent':"Mozilla/5.0 (Macintosh; Intel Mac OS X 10_7_4) AppleWebKit/536.19 (KHTML, like Gecko) Version/6.0 Safari/536.19"}

    def schedules(self, origin, destination, date="", hour=""):
        """Returns a set of train schedules that fit the parameters

        Arguments:
        origin      -- the name of the departure train station
        destination -- the name of the arrival train station
        date        -- the day for the trip (format: YYYY-MM-DD) (default: current day)
        hour        -- the hour for the trip, with a margin of +/-2h before and after (default: current hour is date is not specified, empty string (all day) otherwise)

        Returns:
        - Oject with the parameters used
        - The requestID for subsequent details requests
        - List of results, objects with departure and arrival hours, type of train and the index for a subsequent details request
        """
        
       
        if date == "" and hour == "":
            date = datetime.now().date().strftime("%Y-%m-%d")
            hour = datetime.now().time().hour
        today = datetime.now().date() == date
        # print origin, destination, date,today, hour
        # print "Origin:", origin, "Dest:",destination, "Date:", date, "Hour:",hour
        
        requestParams = {"origin": origin, "destination": destination, "date": date, "hour": hour}
        
        if len(origin.strip()) < 3 or len(destination.strip()) < 3:
            status = "400 Missing or incorrect station names"
            response = {"request":requestParams, "results": [], "status":status}
            return response
             
        
    	r = requests.post('http://www.cp.pt/cp/searchTimetableFromRightTool.do', headers=self.headers, params={'departStation': origin, 'arrivalStation':destination, 'goingDate':date, 'goingTime':hour, 'returningDate':'','returningTime':'','ok':'OK'})
        # print r.cookies
        a = r.content

        f = open('out1.html', 'w')
        f.write(r.content)
        f.close()

        # Grab result text and...
        resulttext = re.search('<td[^>]+tit2white">\s+([^<]+)\s*<', a).group(1).strip().decode("iso-8859-1")

        arr = []
        requestID = ""
        
        # ...check for errors
        if resulttext == u"Não foram encontrados resultados":
            status = "204 No Content"
        elif resulttext == u"":
            status = "400 Bad Request"
        else:
            status = "200 OK"
            start = a.find('<table width="606" border="0" cellspacing="0" cellpadding="0" class="fd_content">')
            end = a.find('<img src="static/images/pix.gif" alt="" width="7" height="10" border="0" /><br />')
            b = a[start:end]
            c = b.split('<td width="18" align="right"><a href="javascript:toggleLine(')
            c.pop(0)
            timeDiff = 15
            i = 1
            h = datetime.now().hour
            m = re.findall('toggleLine\((\d+),(\d+)\)', r.content)
            requestID = m[0][1]
            for d in c:
                m = re.findall('toggleLine\((\d+),(\d+)\)', r.content)
                page = m[0][0]

                e = re.findall('>([^<]+)</td', d)
                
                if (today):
                    td = int(e[2][:2])*60+int(e[2][3:]) - h*60
                    # print "TIMEDIFF",td,
                    if td < -timeDiff:
                        # print "SKIPPING"
                        continue;

                # print "NOT SKIPPING"
                arr.append({'i':i-1, 't':e[1], 'o':e[2], 'd':e[3], 'l':e[4]})
                i+=1

            # store cookies with solutionid and return solutionid
            self.setCookie(requestID, r.cookies)

        response = {"request":requestParams, "requestid": requestID, "results": arr, "status":status}
        return response


    def details(self, requestID, index):
        """Returns details (stops and respective times and trainid) for a specified result of a schedule request

        Arguments:
        requestID   -- the identifier returned on the schedules method
        index       -- the index i of the entry returned by the schedules method

        Returns:
        Ordered list of trains needed to make the trip specified.
        Each train contains type, train number and a list of stops and respective arrival hours
        """
        result = {}
        cks = self.getCookie(requestID)
        if cks is None:
            status = "400 requestid required"
        else:
            r2 = requests.post('http://www.cp.pt/cp/detailSolution.do',headers = self.headers, cookies=cks, params={'page': requestID, 'selectedSolution': index, 'solutionType':'selectedSolution'})
            f = open('out.html', 'w')
            f.write(r2.content)
            f.close()

            soup = BeautifulSoup(r2.content)
            x = soup.find_all("table", {"class" : "fd_content"})[1]

            rows = x.find_all("tr", recursive=False)
            if len(rows) < 5:   # happens if index is bigger
                status = "400 Bad Request"
            else:
                completeRouteRaw = rows[4].find_all("td", recursive=False)
                completeRoute = {
                        "origin": list(completeRouteRaw[3].stripped_strings),
                        "destination": list(completeRouteRaw[4].stripped_strings),
                        "duration": completeRouteRaw[5].string,
                        "type": "".join(list(x.find_all("tr", recursive=False)[4].find_all("td")[2].stripped_strings))
                    }

                listOfTrains = []
                for a in x.find_all("tr", recursive=False)[6].find_all("tr"):
                    if len(list(a.stripped_strings)) > 2:
                        cols = a.find_all("td", recursive=False)
                        entry = []
                        for b in cols[1:]:
                            s = list(b.stripped_strings)
                            if len(s) == 1:
                                entry.append(s[0])
                            elif len(s) > 1:
                                entry.append(s)
                        listOfTrains.append(entry)

                htmlsummary = x.find_all("tr", recursive=False)[6:]

                summary = {"complete": completeRoute, "sections":listOfTrains}

                comboiosraw = x.parent.find_all("table", {"width":"606"})[4:]

                comboios = []


                for c in comboiosraw:
                    if "Comboio n." in c.get_text():
                        ca = re.split("\s{2,}",c.get_text().strip().replace(u"\xa0", ""))

                        paragens = []
                        for p in ca[2:]:
                            paragens.append(p.split("\n"))

                        train = listOfTrains[len(comboios)]

                        comboio = { "type":ca[0],
                                    "train":int(re.findall("(\d+)", ca[1])[0]),
                                    "stops":paragens,
                                    "duration":train[3],
                                    "price":train[4]
                                    }

                        comboios.append(comboio)

                result = {"departure": completeRoute["origin"], 
                          "arrival": completeRoute["destination"],
                          "duration": completeRoute["duration"],
                                    #"date": date, "hour": hour
                          "sections":comboios
                                    }
                status = "200 OK"

        return {"result":result, "status":status}


    def processSummaryRow(row):
        types = ""  # all train types
        a = row.find_all("td")[2]
        for s in a.stripped_strings:
            types += s

        a = row.find_all("table")
        origin = reversed(list(a[0].stripped_strings))  # [time, station]
        destination = reversed(list(a[1].stripped_strings))
        
        duration = row.find_all("td")[9].string

        summary = {"origin": origin, "destination": destination, "type":types, "duration": duration}     
        return summary


    def setCookie(self, rID, cookies):
        """Stores a cookie with the specified id. Only keeps the most recent 100 entries"""
        while (len(self.cookies) > 100):
            self.cookies.pop(0)
        self.cookies.append({"id":rID, "cookies":cookies})

    def getCookie(self, rid):
        """Gets a cookie with the specified id"""
        for i in reversed(self.cookies):
            if (i["id"] == rid):
                return i["cookies"]



    def read(self, request, action):
        """Handles commands from the webserver, runs the appropriate method and returns the data in the specified format

        Arguments:
        action  -- the name of the method (available: schedules, details)
        args    -- a dictionary of parameters as created by BaseHTTPServer
        output  -- the format for the output data; the default is jsonf for indented json, anything else returns unindented json
        """

        args = request.GET
        output = args["output"] if "output" in args else "jsonf"

        result = None
        if action == "schedules":
            try:
                result = self.schedules(args["departure"], args["arrival"], args["date"] if "date" in args else "", args["hour"] if "hour" in args else "")
            except:
                result = self.e("Parameters 'departure' and 'arrival' are required. 'date' and 'hour' are optional.")


        elif action == "details":
            try:
                result = self.details(args["requestid"], args["index"])
            except:
                result = self.e("Parameters 'requestid' and 'index' are required.")

        else:
            result = self.e("Invalid or unspecified action. Valid actions for CP are: 'schedules' and 'details'.")
            # return { "a":"b"}
            # return rc.BAD_REQUEST


        if (result != None):
            return result
            # if (output == "jsonf"):
            #     print json.dumps(result, indent=2)
            # else:
            #     print json.dumps(result)


    def e(self, txt):
        """Generates an error object with the specified message"""
        resp = rc.BAD_REQUEST
        resp.content = [{"error":txt}]
        return resp



if __name__ == "__main__":
    cp = CP()
    #x = cp.schedules("azambuja", "sintra")
    #print json.dumps(x,indent=2)
    #rid=x["requestid"]
    #y=cp.details(rid,1)
    #print json.dumps(y,indent=2)
    x = cp.schedules("azambuja", "alhandra", "2012-12-17", "22")
    print x
    print json.dumps(cp.details(x["requestid"],1), indent=2)
    # print json.dumps(cp.details(x["requestid"],100), indent=2)

# x = cp.schedules("azambuja", "benfica", "2012-06-11", "9")
# print x

# rid = json.loads(x)["requestid"]
# y = cp.details(rid, 0)
# print y
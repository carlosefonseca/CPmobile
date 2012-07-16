import cgi, random, sys
import urlparse
from datetime import datetime
import requests
import re
import json
import sqlite3

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
    	r = requests.post('http://www.cp.pt/cp/searchTimetableFromRightTool.do', headers=self.headers, params={'departStation': origin, 'arrivalStation':destination, 'goingDate':date, 'goingTime':hour, 'returningDate':'','returningTime':'','ok':'OK'})
        # print r.cookies
        a = r.content
        start = a.find('<table width="606" border="0" cellspacing="0" cellpadding="0" class="fd_content">')
        end = a.find('<img src="static/images/pix.gif" alt="" width="7" height="10" border="0" /><br />')
        b = a[start:end]
        c = b.split('<td width="18" align="right"><a href="javascript:toggleLine(')
        c.pop(0)
        arr = [];
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
            arr.append({'i':i-1, 't':e[1], 'd':e[2], 'a':e[3], 'l':e[4]})
            i+=1

        # store cookies with solutionid and return solutionid
        self.setCookie(requestID, r.cookies)
        requestParams = {"departure": origin, "arrival": destination, "date": date, "hour": hour}
        response = {"request":requestParams, "requestid": requestID, "results": arr}
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
        cks = self.getCookie(requestID)
        r2 = requests.post('http://www.cp.pt/cp/detailSolution.do',headers = self.headers, cookies=cks, params={'page': requestID, 'selectedSolution': index, 'solutionType':'selectedSolution'})
        f = open('out.html', 'w')
        f.write(r2.content)
        f.close()

        soup = BeautifulSoup(r2.content)
        x = soup.find_all("table", {"class" : "fd_content"})[1]

        comboiosraw = x.parent.find_all("table", {"width":"606"})[4:]

        comboios = []

        for c in comboiosraw:
            if "Comboio n." in c.get_text():
                ca = re.split("\s{2,}",c.get_text().strip().replace(u"\xa0", ""))

                paragens = []
                for p in ca[2:]:
                    paragens.append(p.split("\n"))

                comboios.append({"tipo":ca[0], "numero":int(re.findall("(\d+)", ca[1])[0]), "paragens":paragens})

        return comboios


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



    def handle(self, action, args, output = "jsonf"):
        """Handles commands from the webserver, runs the appropriate method and returns the data in the specified format

        Arguments:
        action  -- the name of the method (available: schedules, details)
        args    -- a dictionary of parameters as created by BaseHTTPServer
        output  -- the format for the output data; the default is jsonf for indented json, anything else returns unindented json
        """
        result = None
        if action == "schedules":
            try:
                if "day" in args:
                    result = self.schedules(args["departure"][0], args["arrival"][0], args["day"][0])
                else:
                    result = self.schedules(args["departure"][0], args["arrival"][0])
            except:
                result = self.e("Parameters 'departure' and 'arrival' are required. 'day' and 'hour' are optional.")


        elif action == "details":
            try:
                result = self.details(args["requestid"][0], args["index"][0])
            except:
                result = self.e("Parameters 'requestid' and 'index' are required.")


        if (result != None):
            if (output == "jsonf"):
                print json.dumps(result, indent=2)
            else:
                print json.dumps(result)


    def e(self, txt):
        """Generates an error object with the specified message"""
        return {"error":txt}



# cp = CP()
# x = cp.schedules("azambuja", "benfica", "2012-06-11", "9")
# print x

# rid = json.loads(x)["requestid"]
# y = cp.details(rid, 0)
# print y
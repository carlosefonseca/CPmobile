import cgi, random, sys
import urlparse
from datetime import datetime
import requests
import re
import json
import sqlite3

class CP():
    cookies = []
    headers = {'User-Agent':"Mozilla/5.0 (Macintosh; Intel Mac OS X 10_7_4) AppleWebKit/536.19 (KHTML, like Gecko) Version/6.0 Safari/536.19"}

    def schedules(self, origin, destination, date="", hour=""):
        if date == "" and hour == "":
            date = datetime.now().date().strftime("%Y-%m-%d")
            hour = datetime.now().time().hour
        today = datetime.now().date() == date
        # print origin, destination, date,today, hour
    	r = requests.post('http://www.cp.pt/cp/searchTimetableFromRightTool.do', headers=self.headers, params={'departStation': origin, 'arrivalStation':destination, 'goingDate':date, 'goingTime':hour, 'returningDate':'','returningTime':'','ok':'OK'})
        print r.cookies
        a = r.content
        start = a.find('<table width="606" border="0" cellspacing="0" cellpadding="0" class="fd_content">')
        end = a.find('<img src="static/images/pix.gif" alt="" width="7" height="10" border="0" /><br />')
        b = a[start:end]
        c = b.split('<td width="18" align="right"><a href="javascript:toggleLine(')
        c.pop(0)
        arr = {};
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
                if td < -timeDiff:
                    continue;
            arr[page] = ({'i':i-1, 't':e[1], 'd':e[2], 'a':e[3], 'l':e[4]})
            i+=1

        # store cookies with solutionid and return solutionid
        self.setCookie(requestID, r.cookies)
        response = {"departure": origin, "arrival": destination, "date": date, "hour": hour, "requestid": requestID, "results": arr}
        return json.dumps(response)


    def details(self, requestID, page):
        cks = self.getCookie(requestID)
        r2 = requests.post('http://www.cp.pt/cp/detailSolution.do',headers = self.headers, cookies=cks, params={'page': requestID, 'selectedSolution': page, 'solutionType':'selectedSolution'})
        f = open('out.html', 'w')
        f.write(r2.content)
        f.close()
        return r2.content

    def setCookie(self, rID, cookies):
        while (len(self.cookies) > 3):
            self.cookies.pop(0)
        self.cookies.append({"id":rID, "cookies":cookies})

    def getCookie(self, rid):
        for i in reversed(self.cookies):
            if (i["id"] == rid):
                return i["cookies"]
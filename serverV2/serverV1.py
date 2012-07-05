import BaseHTTPServer
import cgi, random, sys
import urlparse
from datetime import datetime
import requests
import re
import json

class Handler(BaseHTTPServer.BaseHTTPRequestHandler):

    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()
        try:
            # redirect stdout to client
            stdout = sys.stdout
            sys.stdout = self.wfile
            self.makepage()
        finally:
            sys.stdout = stdout # restore
        
    def makepage(self):
        cp = CP();
        x = urlparse.parse_qs(self.path[2:])
        print cp.stuff(x["departure"][0], x["arrival"][0], x["day"][0])

class CP():
    def stuff(self, origin, destination, date=datetime.now().date(), hour=""):
        today = datetime.now().date() == date
        # print origin, destination, date,today, hour
    	r = requests.post('http://www.cp.pt/cp/searchTimetableFromRightTool.do',params={'departStation': origin, 'arrivalStation':destination, 'goingDate':date, 'goingTime':hour, 'returningDate':'','returningTime':'','ok':'OK'})
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
        for d in c:
            e = re.findall('>([^<]+)</td', d)
            
            if (today):
                td = int(e[2][:2])*60+int(e[2][3:]) - h*60
                print "td:",td
                if td < -timeDiff:
                    continue;
            arr[i] = ({'i':i, 't':e[1], 'd':e[2], 'a':e[3], 'l':e[4]})
            i+=1
        return json.dumps(arr)

PORT = 8000

httpd = BaseHTTPServer.HTTPServer(("", PORT), Handler)
print "serving at port", PORT
httpd.serve_forever()
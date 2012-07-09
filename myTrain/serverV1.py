import BaseHTTPServer
import cgi, random, sys
import urlparse
from datetime import datetime
import requests
import re
import json
from CP import CP

class Handler(BaseHTTPServer.BaseHTTPRequestHandler):

    cp = CP()

    def do_GET(self):
        try:
            # redirect stdout to client
            stdout = sys.stdout
            sys.stdout = self.wfile
            self.makepage()
        finally:
            sys.stdout = stdout # restore
        
    def makepage(self):
        # cp = CP();
        x = urlparse.parse_qs(self.path[2:])
        if "day" in x:
            print cp.schedules(x["departure"][0], x["arrival"][0], x["day"][0])
        else:
            print cp.schedules(x["departure"][0], x["arrival"][0])


PORT = 8000

httpd = BaseHTTPServer.HTTPServer(("", PORT), Handler)
print "serving at port", PORT
#httpd.serve_forever()
# httpd.handle_request()
# cp = CP()
# print cp.schedules("alverca", "azambuja")
import BaseHTTPServer
import cgi, random, sys
import urlparse
from datetime import datetime
import requests
import re
import json
from CP import CP
from Refer import Refer

class Handler(BaseHTTPServer.BaseHTTPRequestHandler):

    cp = CP()
    refer = Refer()

    def do_GET(self):
        try:
            # redirect stdout to client
            stdout = sys.stdout
            sys.stdout = self.wfile
            lePath = urlparse.urlparse(self.path).path[1:]
            leQuery = urlparse.parse_qs(urlparse.urlparse(self.path).query)
            (targetObjectName, z ,targetActionName) = lePath.partition("/")
            if targetObjectName == "cp":
                self.cp.handle(targetActionName, leQuery)
            elif targetObjectName == "refer":
                self.refer.handle(targetActionName, leQuery)
        finally:
            sys.stdout = stdout # restore

PORT = 8000

httpd = BaseHTTPServer.HTTPServer(("", PORT), Handler)
print "serving at port", PORT
httpd.serve_forever()
httpd.handle_request()
# cp = CP()
# print cp.schedules("alverca", "azambuja")
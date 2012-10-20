from piston.handler import BaseHandler
from piston.utils import rc 


import cgi
import random, sys
import urlparse
from datetime import datetime
import requests
import re
import json

from CP import CP
from Refer import Refer

class Handler(BaseHandler):
    methods_allowed = ('GET',)

    cp = CP()
    refer = Refer()

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
            # try:
            self.e("bu")
            if "day" in args:
                result = cp.schedules(args["departure"], args["arrival"], args["day"])
            else:
                result = cp.schedules(args["departure"], args["arrival"])
            # except:
                # result = self.e("Parameters 'departure' and 'arrival' are required. 'day' and 'hour' are optional.")


        elif action == "scheduleDetails":
            try:
                result = cp.details(args["requestid"], args["index"], args["lines"])
            except:
                result = cp.e("Parameters 'requestid' and 'index' are required.")


        elif action == "departures":
            if ("stationid" in args):
                result = refer.departures(args["stationid"])
            else:
                result = refer.e("Parameter 'stationid' is required.")




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
        resp.content = {"error":txt}
        return resp

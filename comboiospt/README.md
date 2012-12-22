#myTrain — Portuguese Train Schedules (Unofficial) API

by Carlos Fonseca • [@carlosefonseca](http://twitter.com/carlosefonseca) • [Project's GitHub](https://github.com/carlosefonseca/CPmobile/tree/v2/comboiospt)

----

This API extracts information from the websites [CP.pt](http://cp.pt) (schedules for CP trains) and [Refer.pt](http://refer.pt) (Train arrivals and departures at stations). Eventually, other train companies might be added.

The API currently contains the following methods:

- [CP / Schedules](#cpsch)
- [CP / Details](#cpdet)
- [Refer / Departures](#referd)

<a id="cpsch"></a>
## CP / Schedules

    /cp/schedules?origin=<station-name>&destination=<station-name>[&date=<YYYY-MM-DD>][&hour=<HH>]

Returns a list of CP possible "trips" between the two stations at the given date and time. If no date/time are given, the current ones will be used. Please note that cp.pt returns results starting at 2 hours before and until 2 hours after the requested hour.

You should use the station names as used by cp.pt, as they are fed directly to it.

The response contains an identifier, `requested`, from cp.pt, that is required for the `details` requests, and a list of "trip possibilities" that satisfy the request.

Please note this request doesn't specify if multiple trains and transfers are required, the `details` request is needed for that. This request can only tell you if multiple types of trains are required.

- `i` is the index of the train, for `details`
- `t` is the types of trains, like `U` for Urban or `R+U` for Regional and Urban. The full list according to cp.pt:

      U	  Urbanos
	  AP  Alfa Pendular
	  IC  Intercidades
	  R   Regional
	  IR  Inter-Regional
	  IN  Internacional
   	  TC  Transporte Complementar

- `l` is the duration of the trip
- `o` is the time at the origin, the time of departure
- `d` is the time at the destination, the time of arrival


###Example:

####Request:

	/cp/schedules?origin=azambuja&destination=benfica&date=2012-12-21&hour=12

####Response (shortened):

    {
       "status":"200 OK",
       "request":{
          "origin":"azambuja",
          "date":"2012-12-21",
          "destination":"benfica",
          "hour":"12"
       },
       "requestid":"1356195717737",
       "results":[
          {
             "i":0,
             "l":"0h54",
             "t":"R+U",
             "o":"10h33",
             "d":"11h27"
          },
          {
             "i":1,
             "l":"1h09",
             "t":"U",
             "o":"10h48",
             "d":"11h57"
          },
          {
             "i":2,
             "l":"0h53",
             "t":"R+U",
             "o":"11h34",
             "d":"12h27"
          }
       ]
    }
   

<a id="cpdet"></a>
## CP / Train Details

	/cp/details?requestid=<id-from-schedules>&i=<index>

After requesting a schedule, you can request details for each of the trips by providing the `requested` and the `index`.

This will return all the trains for this trip and, for each, the type, the price, the duration, and the times and stations of each stop.

The trains are ordered, so the ending station of a train is the first of the next one.



###Example:

####Request:

	/cp/details?requestid=1356195717737&i=2

####Response:
	
	{
	   "status":"200 OK",
	   "result":{
		  "origin":[
	         "11h34",
	         "Azambuja"
	      ],
	      "destination":[
	         "12h27",
	         "Benfica"
	      ],
	      "duration":"0h53",
	      "sections":[
	         {
	            "duration":"0h28",
	            "price":"\u20ac3,85",
	            "train":4414,
	            "type":"Regional",
	            "stops":[
	               [
	                  "Azambuja",
	                  "11h34"
	               ],
	               [
	                  "Vila Franca De Xira",
	                  "11h46"
	               ],
	               [
	                  "Alverca",
	                  "11h52"
	               ],
	               [
	                  "Oriente",
	                  "12h02"
	               ]
	            ]
	         },
	         {
	            "duration":"0h16",
	            "price":"\u20ac2,05",
	            "train":18248,
	            "type":"Urbano",
	            "stops":[
	               [
	                  "Oriente",
	                  "12h11"
	               ],
	               [
	                  "Braco De Prata",
	                  "12h14"
	               ],
	               [
	                  "Roma - Areeiro",
	                  "12h18"
	               ],
	               [
	                  "Lisboa - Entrecampos",
	                  "12h20"
	               ],
	               [
	                  "Sete Rios",
	                  "12h23"
	               ],
	               [
	                  "Benfica",
	                  "12h27"
	               ]
	            ]
	         }
	      ]
	   }
	}
	

<a id="referd"></a>
##Refer / Departures

	/refer/departures?stationid=<refer's station code>

This method gets the train departures from a station.

For each train the origin and destination stations are specified, its type, the scheduled time of arrival and the train's status.

Please use the list on `/stations.csv` to match the names to the ID's. Refer.pt only works with the IDs and I feel it's best to do the matching on the client side, where the user can select the correct station and let the server be as quick as possible.

This are the possible status codes:

- `À tabela` – Train on schedule
- `Atrasado: # minutos` – Train delayed by # minutes beyond the scheduled time
- `SUPRIMIDO` – Train canceled

Please note that, sometimes, a train is not considered delayed but it still appears on the listing despite its scheduled time is already in the past, usually the train is a couple of minutes late. It's possible that requesting again might get you a delayed message.

Also note that canceled trains usually stick around on the listings for some hours after their scheduled time.


###Example:

####Request:

	/refer/departures?stationid=9431237

####Response:

	{
	   "request":{
	      "station":"9431237"
	   },
	   "results":[
	      {
	         "origin":[
	            "9433001",
	            "Azambuja"
	         ],
	         "status":"\u00c0 tabela",
	         "hour":"19h08",
	         "destination":[
	            "9467025",
	            "Alc\u00e2ntara-Terra"
	         ],
	         "train":"16550",
	         "type":"SUBURB"
	      },
	      {
	         "origin":[
	            "9467025",
	            "Alc\u00e2ntara-Terra"
	         ],
	         "status":"\u00c0 tabela",
	         "hour":"19h22",
	         "destination":[
	            "9433001",
	            "Azambuja"
	         ],
	         "train":"16452",
	         "type":"SUBURB"
	      },
	      {
	         "origin":[
	            "9433001",
	            "Azambuja"
	         ],
	         "status":"\u00c0 tabela",
	         "hour":"19h38",
	         "destination":[
	            "9467025",
	            "Alc\u00e2ntara-Terra"
	         ],
	         "train":"16552",
	         "type":"SUBURB"
	      },
	      {
	         "origin":[
	            "9467025",
	            "Alc\u00e2ntara-Terra"
	         ],
	         "status":"\u00c0 tabela",
	         "hour":"19h52",
	         "destination":[
	            "9433001",
	            "Azambuja"
	         ],
	         "train":"16454",
	         "type":"SUBURB"
	      }
	   ]
	}
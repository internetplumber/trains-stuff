#!/usr/local/bin/python3

#
# Show the list of departures from a station, optionally filtered by
# destination.
#     dep-board.py ORIGIN [DEST] [OFFSET]
#
# ORIGIN and DEST should both be three character CRS codes.
# OFFSET is the offset from the current time (in minutes, <120) to view the
# departure boards.
#

from zeep import Client
from zeep import xsd
import sys

LDB_TOKEN = ''
WSDL = 'http://lite.realtime.nationalrail.co.uk/OpenLDBWS/wsdl.aspx?ver=2017-10-01'
DEST = ''
OFFSET = 0
destSta = ''

if len(sys.argv) < 2:
    print("Please supply an origin station.")
    sys.exit()
if len(sys.argv) >= 2:
    ORIGIN = sys.argv[1]
if len(sys.argv) >= 3:
    DEST = sys.argv[2]
if len(sys.argv) >= 4:
    OFFSET = sys.argv[3]

client = Client(wsdl=WSDL)
header = xsd.Element(
    '{http://thalesgroup.com/RTTI/2013-11-28/Token/types}AccessToken',
    xsd.ComplexType([
        xsd.Element(
            '{http://thalesgroup.com/RTTI/2013-11-28/Token/types}TokenValue',
            xsd.String()),
    ])
)
header_value = header(TokenValue=LDB_TOKEN)
if len(DEST) > 0:
    res = client.service.GetDepBoardWithDetails(numRows=9, crs=ORIGIN, filterCrs=DEST, timeOffset=OFFSET,
                                                _soapheaders=[header_value])
    destSta = res.filterLocationName
else:
    res = client.service.GetDepBoardWithDetails(numRows=9, crs=ORIGIN, _soapheaders=[header_value])

if len(destSta) > 0:
    print("Departures from " + res.locationName + " to " + destSta)
    print("=" * len("Departures from " + res.locationName + " to " + destSta))
else:
    print("Departures from " + res.locationName)
    print("=" * len("Departures from " + res.locationName))
services = res.trainServices.service
i = 0
while i < len(services):
    t = services[i]
    print(t.std + " to " + t.destination.location[0].locationName + " - " + t.etd +
        " (" + str(t.length) + " coaches)")
    cps = t.subsequentCallingPoints.callingPointList[0].callingPoint
    j = 0
    while j < len(cps):
        print("    {0:25s} {1:6s} {2:s}".format(cps[j].locationName, cps[j].st, cps[j].et))
        j += 1
    i += 1
print("Generated at " + res.generatedAt.ctime())
print("Powered by National Rail Enquiries.")

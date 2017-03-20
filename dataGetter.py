from pprint import pprint
from yahoo_finance import Share
from datetime import datetime, timedelta
import time
import sys
import subprocess
import json
from os.path import expanduser
home = expanduser("~")



market = sys.argv[1]
direction = sys.argv[2]

class DataGetter():
    
    def __init__(self, market, direction):
        self.market = market
        self.direction = direction

        f = open(home + "/Dropbox/wsj_algo/data/" + self.market + "_" + self.direction + ".txt", "r")
        txt = f.read()
        raw_data = json.loads(txt.replace("'", "\""))
        f.close()

        self.data = raw_data

    def processData(self):
        tranformedData = []
        i = 0
        for el in self.data:
            print "doing #" + str(i + 1) + "/" + str(len(self.data))
            result = makeOb(el)
            tranformedData.append(result)
            i += 1

    def makeFile(self, tranformedData):
        jsonResult = json.dumps(tranformedData)
        f = open(home + "/Dropbox/wsj_algo/data/" + self.market + "-" + self.direction + ".txt", "w")
        f.write(jsonResult)
        f.close()
    
    def run(self):
        for el in self.data:
            print el

DataGetter(market, direction).run()

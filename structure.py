from pprint import pprint
import sys
import json
import numpy as np
import scipy as sp
from scipy import stats
from os.path import expanduser
from datetime import datetime, timedelta
home = expanduser("~")

market = sys.argv[1]
side = sys.argv[2]

class Structurer():

    def __init__(self, market, side):
        self.market = market
        self.side = side

        f = open(home + "/Dropbox/wsj_algo/data/" + self.market + "-" + self.side + ".txt", "r")
        txt = f.read()
        f.close()

        self.raw_data = json.loads(txt)

    def extract(self, ob):
        priceData = ob["raw_data"]
        startDate = datetime.strptime(str(ob["date"]), "%Y-%m-%d")
        startPrice = float(priceData[len(priceData) - 1]["Close"])
        for i in range(len(priceData)):
            dayData = priceData[i]
            dayRange = str(datetime.strptime(str(dayData["Date"]), "%Y-%m-%d") - startDate).split(" ")[0]
            #print dayRange, len(priceData)
            if dayRange == "0:00:00":
                dayRange = 0

            high = float(dayData["High"])
            low = float(dayData["Low"])
            close = float(dayData["Close"])
            openPrice = float(dayData["Open"])
            volatility = high - low
            upward_move = (high - openPrice) / float(openPrice)
            upward_move = upward_move * 100
            downward_move = (low - openPrice) / float(openPrice)
            downward_move = downward_move * 100
            move_next_close = (close - startPrice) / float(startPrice)
            move_next_close = move_next_close * 100
            intraday_move = (close - openPrice) / float(openPrice)
            intraday_move = intraday_move * 100
            ob["downward_move_" + str(dayRange)] = downward_move
            ob["upward_move_" + str(dayRange)] = upward_move
            ob["volatility_" + str(dayRange)] = volatility
            ob["move_next_close_" + str(dayRange)] = move_next_close
            ob["intraday_move_" + str(dayRange)] = intraday_move
            ob["open_" + str(dayRange)] = openPrice
            ob["high_" + str(dayRange)] = high
            ob["low_" + str(dayRange)] = low
            ob["close_" + str(dayRange)] = close

        return ob

    def run(self):
        structuredData = []
        i = 0
        for el in self.raw_data:
            print i, len(self.raw_data)
            priceData = el["raw_data"]
            if len(priceData) > 0:
                try:
                    ob = self.extract(el)
                    structuredData.append(ob)
                except Exception as e:
                    print str(e)
            i += 1

        self.makeFile(structuredData)

    def makeFile(self, tranformedData):
        jsonResult = json.dumps(tranformedData)
        f = open(home + "/Dropbox/wsj_algo/data/" + self.market + "-" + self.side + "_structured.txt", "w")
        f.write(jsonResult)
        f.close()


Structurer(market, side).run()

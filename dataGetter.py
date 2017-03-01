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

def fprint(message):
    print message
    sys.stdout.flush()

def makeOb(ob):
    internal_ob = {}
    internal_ob["position"] = ob["position"]
    internal_ob["high"] = 0
    internal_ob["ticker"] = ob["ticker"]
    internal_ob["move"] = ob["move"]
    internal_ob["move_next_open"] = 0
    internal_ob["move_next_close"] = 0
    internal_ob["volume"] = ob["volume"]
    internal_ob["date"] = ob["date"]
    internal_ob["open"] = 0
    internal_ob["close"] = 0
    internal_ob["lowest"] = 0

    status = 0
    errors = 0
    while status < 1:
        try:
            result = extractData(ob["date"], ob["position"], ob["ticker"])
            internal_ob.update(result)
            status = 1
        except Exception as e:
            if errors < 5:
                fprint(str(e))
                time.sleep(10)
                errors += 1
            else:
                status = 1


    
    if internal_ob["move_next_close"] == 0:
        pprint(internal_ob)
    return internal_ob

def extractData(date, position, ticker):
    internal_ob = {}

    stock = Share(ticker)

    beginning = datetime.strptime(date, "%Y-%m-%d")
    if beginning.isoweekday() in range(1, 5):
        nextDay = beginning + timedelta(days=1)
    elif beginning.isoweekday() == 5:
        nextDay = beginning + timedelta(days=3)
    nextDay = nextDay.strftime("%Y-%m-%d")

    try:
        data = stock.get_historical(date, nextDay)
        if len(data) != 2:
            raise Exception("too early data")
            fprint(data)
    except Exception as e:
        fprint(str(e))
        data = [{"Open": 0, "Close": 0}, {"Open": 0, "Close": 0}]

    opening = float(data[1]["Open"])
    close = float(data[1]["Close"])

    pop = 0
    rise = 0
    high = 0
    low = 0
    try:
        priceData = data[0]
        high = (float(priceData["High"]) - close) / float(close) 
        highest = high * 100
        pop = (float(priceData["Open"]) - close) / float(close) 
        pop = pop * 100
        rise = (float(priceData["Close"]) - close) / float(close) 
        rise = rise * 100
        low = (float(priceData["Low"]) - close) / float(close) 
        low = low * 100
    except Exception as e:
        fprint(e)
        priceData = {"Open": 0, "Close": 0, "Low": 0}

    nextDayOpen = float(priceData["Open"])
    nextDayClose = float(priceData["Close"])

    internal_ob["highest"] = highest
    internal_ob["move_next_open"] = pop
    internal_ob["move_next_close"] = rise
    internal_ob["open"] = opening
    internal_ob["close"] = close
    internal_ob["lowest"] = low
    internal_ob["nextDay_open"] = nextDayOpen
    internal_ob["nextDay_close"] = nextDayClose

    return internal_ob

def getData():
    f = open(home + "/Dropbox/wsj_algo/data/" + market + "_" + str(direction) + ".txt", "r")
    txt = f.read()
    raw_data = json.loads(txt.replace("'", "\""))
    f.close()

    return raw_data

def processData():
    tranformedData = []
    i = 0
    listOfStuff = getData()
    for el in listOfStuff:
        fprint("doing #" + str(i + 1) + "/" + str(len(listOfStuff)))
        result = makeOb(el)
        tranformedData.append(result)
        i += 1

    jsonResult = json.dumps(tranformedData)
    f = open(home + "/Dropbox/wsj_algo/data/" + market + "-" + direction + ".txt", "w")
    f.write(jsonResult)
    f.close()

processData()

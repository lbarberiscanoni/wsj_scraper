from pprint import pprint
import sys
import json
import numpy as np
import scipy as sp
from scipy import stats
from os.path import expanduser
home = expanduser("~")

market = sys.argv[1]
side = sys.argv[2]

def getData():
    f = open(home + "/Dropbox/wsj_algo/data/" + market + "-" + side + ".txt", "r")
    txt = f.read()
    raw_data = json.loads(txt.replace("'", "\""))
    f.close()

    return raw_data

def generate():
    data = []
    for el in getData():
        opening = (el["move_next_open"] / float(100)) * el["close"]
        opening = opening + el["close"]
        nextClose = (el["move_next_close"] / float(100)) * el["close"]
        nextClose = nextClose + el["close"]
        try:
            move = (nextClose - opening) / float(opening)
            move = move * 100
        except:
            move = 0
        el["nextDay_move"] = move
        el["highest"] = el["high"]
        el["lowest"] = el["lowest"]
        data.append(el)

    return data

def makeFile(tranformedData):
    jsonResult = json.dumps(tranformedData)
    f = open(home + "/Dropbox/wsj_algo/data/" + market + "-" + side + "-test-post.txt", "w")
    f.write(jsonResult)
    f.close()

def confidenceInterval(data, confidence=0.95):
    a = 1.0*np.array(data)
    n = len(a)
    m, se = np.mean(a), stats.sem(a)
    h = se * sp.stats.t._ppf((1+confidence)/2., n-1)

    return m, m-h, m+h

def check():
    f = open(home + "/Dropbox/wsj_algo/data/" + market + "-" + side + "-test-post.txt", "r")
    txt = f.read()
    raw_data = json.loads(txt.replace("'", "\""))
    f.close()

    moves = [x["nextDay_move"] for x in raw_data]
    print confidenceInterval(moves)

def test():
    f = open(home + "/Dropbox/wsj_algo/data/" + market + "-" + side + "-test-post.txt", "r")
    txt = f.read()
    raw_data = json.loads(txt.replace("'", "\""))
    f.close()

    returnList = []
    for x in raw_data:
        stopLoss = -10
        slippage = 1
        threshold = 3
        if x["move_next_open"] < threshold:
            move = x["nextDay_move"] * -1
            move -= slippage
        elif x["move_next_open"] > threshold:
            move = x["nextDay_move"]
            move -= slippage
        else:
            move = 0
        if move < stopLoss:
            move = stopLoss
        returnList.append(move)

    print confidenceInterval(returnList)

makeFile(generate())
#test()

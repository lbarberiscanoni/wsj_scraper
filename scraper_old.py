from pprint import pprint
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from datetime import datetime, timedelta
import time
import sys
import json
from os.path import expanduser

home = expanduser("~")


market = sys.argv[1]
direction = sys.argv[2]

class Scraper():

    def __init__(self, market, direction):
        self.browser = webdriver.Chrome()
        self.market = market
        self.direction = direction

    def getUrl(self, date):
        if self.market == "nyse":
            if self.direction == "long":
                base_url = "http://online.wsj.com/mdc/public/page/2_3021-gainnyse-gainer-" + date.replace("-", "") + ".html?mod=mdc_pastcalendar"
            elif self.direction == "short":
                base_url = "http://online.wsj.com/mdc/public/page/2_3021-losenyse-loser-" + date.replace("-", "") + ".html?mod=mdc_pastcalendar"
        elif self.market == "nasdaq":
            if self.direction == "long":
                base_url = "http://online.wsj.com/mdc/public/page/2_3021-gainnnm-gainer-" + date.replace("-", "") + ".html?mod=mdc_pastcalendar"
            elif self.direction == "short":
                base_url = "http://online.wsj.com/mdc/public/page/2_3021-losennm-loser-" + date.replace("-", "") + ".html?mod=mdc_pastcalendar"
        elif self.market == "arca":
            if self.direction == "long":
                base_url = "http://online.wsj.com/mdc/public/page/2_3021-gainarca-gainer-" + date.replace("-", "") + ".html?mod=mdc_pastcalendar"
            elif self.direction == "short":
                base_url = "http://online.wsj.com/mdc/public/page/2_3021-losearca-loser-" + date.replace("-", "") + ".html?mod=mdc_pastcalendar"
        elif self.market == "composite":
            if self.direction == "long":
                base_url = "http://online.wsj.com/mdc/public/page/2_3021-gaincomp-gainer-" + date.replace("-", "") + ".html?mod=mdc_pastcalendar"
            elif self.direction == "short":
                base_url = "http://online.wsj.com/mdc/public/page/2_3021-losecomp-loser-" + date.replace("-", "") + ".html?mod=mdc_pastcalendar"

        return base_url
    
    def extractData(self, date, row, position):
        internal_ob = {}
        rowData = row.text.split("(")[1].split(" ")
        ticker = str(rowData[0]).replace(")", "").replace("@", "")
        perChange = float(str(rowData[3]))
        volume = int(rowData[4].replace(",", ""))

        beginning = datetime.strptime(date, "%Y-%m-%d")
        if beginning.isoweekday() in range(1, 6):
            nextDay = beginning + timedelta(days=1)
        elif beginning.isoweekday() == 5:
            nextDay = beginning + timedelta(days=3)
        elif beginning.isoweekday() == 6:
            nextDay = beginning + timedelta(days=2)
        elif beginning.isoweekday() == 7:
            nextDay == beginning + timedelta(days=1)
        nextDay = nextDay.strftime("%Y-%m-%d")

        internal_ob["position"] = position
        internal_ob["ticker"] = ticker
        internal_ob["move"] = perChange
        internal_ob["volume"] = volume
        internal_ob["date"] = date
        internal_ob["nextDay"] = nextDay

        return internal_ob

    def top100(self, date):
        base_url = self.getUrl(date)
        self.browser.get(base_url)

        rows = self.browser.find_elements_by_css_selector(".mdcTable tbody tr")
        #removing extra rows that don't contain data
        for i in range(0, len(rows) - 100):
            rows.pop(i)
        position = 1
        obList = []
        for row in rows:
            print "doing #" + str(position) + "/" + str(len(rows))
            try:
                result = self.extractData(date, row, position)
                obList.append(result)
            except Exception as e:
                internal_ob = {}
                internal_ob["position"] = position
                internal_ob["ticker"] = "N/A"
                internal_ob["move"] = "0"
                internal_ob["volume"] = "0"
                internal_ob["date"] = date
                internal_ob["nextDay"] = "0"

                obList.append(internal_ob)
            position += 1
        
        return obList

    def main(self):
        today = str(datetime.now()).split(" ")[0]
        print today
        obList = []
        end = datetime(2007, 5, 1)
        totalDaysToDo = int((datetime.now() - end).days)
        for i in range(0, totalDaysToDo):
            try:
                print str(i)
                beginning = datetime.strptime(today, "%Y-%m-%d")
                date = beginning - timedelta(days=i)
                if date.isoweekday() in range(1, 6):
                    date_formatted = date.strftime("%Y-%m-%d").split(" ")[0]
                    print "doing " + str(date_formatted)
                    result = self.top100(date_formatted)
                    obList += result
                else:
                    print "skipping " + str(date)
            except Exception as e:
                 print str(e)
                 if "timeout" in str(e):
                    self.browser.refresh()
                    beginning = datetime.strptime(today, "%Y-%m-%d")
                    date = beginning - timedelta(days=i)
                    if date.isoweekday() in range(1, 6):
                        date_formatted = date.strftime("%Y-%m-%d").split(" ")[0]
                        print "doing " + str(date_formatted)
                        result = self.top100(date_formatted)
                        obList += result
                    else:
                        print "skipping " + str(date)

        jsonResult = json.dumps(obList)
        f = open(home + "/Dropbox/wsj_algo/data/" + self.market + "_" + self.direction + ".txt", "w")
        f.write(jsonResult)
        f.close()

Scraper(market, direction).main()

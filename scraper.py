import pandas as pd
from datetime import datetime, timedelta
import sys
from os.path import expanduser
home = expanduser("~")

market = sys.argv[1]
direction = sys.argv[2]

class Scraper():

    def __init__(self, market, direction):
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

    def scrapeData(self, url):
        dfs = pd.read_html(url, header=0)
        spec = dfs[1]
        spec["Ticker"] = spec["Issue(Roll over for charts and headlines)"].str.split("(").str[1].str.replace(")", "")
        spec["Position"] = spec[spec.columns[0]]
        spec["Price"] = spec["Price"].str.replace("$", "")
        spec.drop(spec.columns[1], axis=1, inplace=True)
        spec.drop(spec.columns[0], axis=1, inplace=True)
        
        jsonData = spec.to_json(orient="records")

        return jsonData

    def makeFile(self, obList):
        jsonResult = json.dumps(obList)
        f = open(home + "/Dropbox/wsj_algo/data/" + self.market + "_" + self.direction + ".txt", "w")
        f.write(jsonResult)
        f.close()
    
    def run(self):
        today = str(datetime.now()).split(" ")[0]
        print today
        obList = []
        end = datetime(2007, 5, 1)
        totalDaysToDo = int((datetime.now() - end).days)
        for i in range(0, totalDaysToDo):
            print str(i)
            beginning = datetime.strptime(today, "%Y-%m-%d")
            date = beginning - timedelta(days=i)
            if date.isoweekday() in range(1, 6):
                date_formatted = date.strftime("%Y-%m-%d").split(" ")[0]
                print "doing " + str(date_formatted)
                result = self.scrapeData(self.getUrl(date_formatted))
                obList.append(result)
            else:
                print "skipping " + str(date)

        self.makeFile(obList)

Scraper(market, direction).run()

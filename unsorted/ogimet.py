# https://github.com/iuiuiu-wayy/Ogimet

import requests, csv
import numpy as np
from lxml import html
from calendar import monthrange
from dateutil.rrule import rrule, MONTHLY, DAILY
from datetime import datetime
import os
from sys import argv

class Downloader():
    """docstring for Downloader."""

    def __init__(self):
        if os.getcwd().__contains__("\\"):
            self.sep = "\\"
        else:
            self.sep = "/"

        self.temptcolnames = ['Max', 'Min', 'Avg']
        self.windcolnames = ['Dir.', 'Int.']
        self.sumcolnames = ['03', '06', '09', '12', '15', '18', '21', '24']
        self.comb = {}

    def month_iter(self, start_month, start_year, end_month, end_year):
        start = datetime(start_year, start_month, 1)
        end = datetime(end_year, end_month, 1)
        r = ((d.month, d.year) for d in rrule(MONTHLY,dtstart=start, until=end))
        return r

    def tryGetTable(self, tree, year, month, attempt=10):
        if attempt == 0:
            return "Fail"
        try:
            return tree.xpath('//table[@border="0"]')[0]
        except:
            tree = self.requestData(self.linkConstructor(year, month))
            self.tryGetTable(tree, year, month, attempt=attempt-1)

    def requestData(self,link, attempt=10):
        if attempt == 0:
            return "Fail"
        page = requests.get(link)
        noSummary=page.content.__str__().__contains__('summary')
        if any( [page.status_code != 200, not noSummary ]):
            requestData(link, attempt=attempt-1)
        tree = html.fromstring(page.content)
        return tree

    def running_all(self, end_year, end_month, start_year=2000, start_month=1,\
    stationid="97240", location=os.getcwd()):
        self.stationid = stationid
        #make directory
        dir_name = stationid + "-" + str(start_year) + str(start_month) + "-"+\
         str(end_year)+ str(end_month)
        try:
            os.mkdir(location + self.sep + dir_name )
        except FileExistsError:
            print("direcory already exist")
        self.location = location + self.sep + dir_name

        for m in self.month_iter(start_month, start_year, end_month, end_year):
            print("running " + m[1].__str__() + "-" + m[0].__str__() )
            #print(m[0])
            #print(m[1])
            self.completeRun(m[1], m[0])

    def linkConstructor(self, year, month):
        link = "https://www.ogimet.com/cgi-bin/gsodres?lang=en&ind="+ \
        self.stationid +"&ndays=" + monthrange(year, month)[1].__str__() + \
        "&ano=" + year.__str__() + "&mes=" + "%02d" % month + "&day=" + \
        "%02d" % monthrange(year, month)[1] + "&hora=00&ord=REV&Send=Send"
        return link

    def requestData(self,link, attempt=10):
        if attempt == 0:
            return "Fail"
        page = requests.get(link)
        noSummary= page.content.__str__().__contains__('summary')
        if any( [page.status_code != 200, not noSummary ]):
            self.requestData(link, attempt=attempt-1)
        tree = html.fromstring(page.content)
        return tree

    def completeRun(self, year, month):
        link = self.linkConstructor(year, month)
        print(link)
        data = self.requestData(link)
        self.writeData(data, year, month, self.location, '')

    def failDetector(self, year, month):
        with open('report.log', 'a') as report:
            report.write(year.__str__() + "-" + month.__str__() + "\n")

    def getcolum(self, table):
        colnames = []
        for a in table.getchildren()[1][0][:]:
            if a.text_content().__contains__("Temperature"):
                for b in table.getchildren()[1][1]:
                    if self.temptcolnames.__contains__(b.text_content()):
                        col = a.text_content() + b.text_content()
                        colnames.append(col)
            elif a.text_content().__contains__("Wind"):
                for b in table.getchildren()[1][1]:
                    if self.windcolnames.__contains__(b.text_content()):
                        col = a.text_content() + b.text_content()
                        colnames.append(col)
            elif a.text_content().__contains__("summary"):
                for c in self.sumcolnames:
                    col = a.text_content() + c
                    colnames.append(col)
            else:
                col = a.text_content()
                colnames.append(col)

        #print("colnames")
        #print(colnames)
        return colnames

    def writeData(self,tree, year, month, location, basename=''):

        if tree == "Fail":
            self.failDetector(year, month)
            return 0
        table = self.tryGetTable(tree, year, month)
        if table == "Fail":
            self.failDetector(year, month)
            return 0

        colnames = self.getcolum(table)

        caption = table.getchildren()[0]
        tr = table.getchildren()[2:monthrange(year, month)[1] + 2]
        monthly = 0
        na = 0
        for a in tr[::-1]:
            data = {}
            id = 0
            for colname in colnames:
                try:
                    data[colname] = a.getchildren()[id].text_content()
                except:
                    data[colname] = 'No Data'
                id = id + 1

            name = self.sep + basename + 'data' + year.__str__() + '-' +\
            "%02d" % month + '-' + data['Date'].split("/")[1] + '.csv'
            self.comb[name]=data


            for key, value in data.items():
                timestamp = year.__str__() + "-%02d-" % month + \
                data['Date'].split("/")[1]
                self.writecsv(key, timestamp , value)

                #### additional for botir requests
                if key.__contains__("Prec"):
                    if value == 'Tr':
                        value = 0

                    if any ( [value == '----' , value == 'No data']):
                        value = 'NA'
                        na = na + 1
                    else:
                        monthly = monthly + float(value)

        #### write monthly data
        filename = self.location + self.sep + "monthly-prec" + ".csv"
        filename2 = self.location + self.sep + "monthly-prec-na" + ".csv"
        time = year.__str__() + "-%02d" % month
        with open(filename, 'a') as csv_file:
            csv_file.write("%s, %s\n" % (time, str(monthly)))

        with open(filename2, 'a') as csv_file2:
            csv_file2.write("%s, %s\n" % (time, str(na)))

    def writecsv(self, key, timestamp, val):
        #self.comb[filename] = dict
        if not key.endswith("."):
            filename = self.location + self.sep + key + ".csv"
        elif key.__contains__("/"):
            newkey = key.split("/")[0] + key.split("/")[1]
            filename = self.location + self.sep + newkey + "csv"
        else:
            filename = self.location + self.sep + key + "csv"


        with open(filename, 'a') as csv_file:
            if any ( [val == '----' , val == 'No data']):
                val = 'NA'
            if val == 'Tr':
                val = 0
            csv_file.write("%s, %s\n" % (timestamp, val))

if __name__ == '__main__':
    cont = True
    # try:
    #     script, yend, mend, ystart, mstart, stationid = argv
    # except:
    #     format = '(end-year) (end-month) (start-year) (start-month) (stationid)'
    #     print("usage >>>> python ogimet.py " + format)
    #     print("example >>>>> python ogimet.py 2019 5 2019 1 97240")
    #     print(" WARNING!!!!: DO NOT OPEN THE FILE WHILE DOWNLOADED!!!!")
    #     cont = False
    if cont:
        yend, mend, ystart, mstart, stationid = 2023,7,2000,1,"485500-99999"
        D = Downloader()
        #D.running_all(2019, 5, start_year=2019, start_month=1,\
        #stationid="97240"
        D.running_all(int(yend), int(mend), int(ystart), int(mstart), stationid)
        print("Enjoy you data :) ")

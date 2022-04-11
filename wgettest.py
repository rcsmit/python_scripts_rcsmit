# import urllib
# urllib.urlretrieve("http://google.com/index.html", filename="index.html")


# C:/Users/rcxsm/AppData/Local/Programs/Python/Python38/python.exe -m wget stns=235:280:260&vars=VICL:PRCP&start=19700101&end=20090818 http://projects.knmi.nl/klimatologie/daggegevens/getdata_dag.cgi

import wget
url = 'http://www.futurecrew.com/skaven/song_files/mp3/razorback.mp3'
filename = wget.download(url)

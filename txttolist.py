import csv

list =[]

with open('workvalues.csv', 'r') as fd:
    reader = csv.reader(fd)
    for rx in reader:
        # do something
       
        if rx not in list: 
            list.append(rx)
            print (rx)
    
    print (list)
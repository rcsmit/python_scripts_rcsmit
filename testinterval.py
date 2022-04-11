for x in range (10,300):
    if x<20:
        interval_ = 1
    else:

        interval_=  (int (((x / 50)))*5)
    print (str(x)+ " - " + str(interval_))

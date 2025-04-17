from datetime import datetime


import pandas as pd

def calculate(y, a_,b_):

    date_format = "%d/%m/%Y"
    # a = datetime.strptime(a_, date_format)
    # b = datetime.strptime(b_, date_format)
    # print (b)

    
    # delta = b - a


    a = pd.to_datetime(a_, format=date_format)
    b = pd.to_datetime(b_, format=date_format)
    delta = (b-a).days

    gamma = 365 - delta 

    

    #print (f"{y}: in Europa {delta} | in Azie {gamma}")
    print (f"[{y},{delta},{gamma}],")


def main():
    list = [[2017, "1/3/2017", "1/11/2017"],
    [2018, "5/3/2018", "5/11/2018"],
    [2019, "3/4/2019", "11/11/2019"],
    [2020, "30/6/2020", "31/12/2020"],
    [2021, "1/1/2021", "15/11/2021"],
    [2022, "21/5/2022", "8/11/2022"], 
    [2023, "20/02/2023", "20/10/2023"], 
    ]
    print ("[")

    for l in list:
        calculate (l[0], l[1], l[2])
    print ("]")
main()
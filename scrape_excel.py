# Script to scrape a directory with excel files

# Import libraries

import os

import pandas as pd


def load_csv():
    sun = "C:\Users\rcxsm\Documents\python_scripts\in\zonnecollectoren_rznstrt_5\zonnecollectoren.csv"
    
def do_your_thing(file):
    print (file)
    workbook = pd.read_excel(file)
   
    h = workbook.head()
    #print (workbook)
    #print (h)
    month_ = (workbook['Smit Monthly Report'].iloc[2])
    for i in range(3,34):
        column = f"Unnamed: {i}"
        try:
            day = (workbook[column].iloc[15])
          
            year = month_[0:4]
            month = month_[-2:]
            value = (workbook[column].iloc[16])
            output =  (f"{int(day)}-{month}-{year},{value}")
            
            with open('zonnecollectoren.csv', 'a') as f:
                f.write(output)
                f.write('\n')
            # (f"{month}-{int(day)},{value}")
        except:
            pass
def main():
    ######################################################################

   
    dir_name = r"C:\Users\rcxsm\Documents\python_scripts\in\zonnecollectoren_rznstrt_5"
    to_do = "single_directory"  

    if to_do == "single_directory":
        rootdir = dir_name
        print(f"Browsing {dir_name}")
        lengte = len(os.listdir(dir_name))
        n = 1
        os.chdir(dir_name)  # change directory from working dir to dir with files

        for file in os.listdir(dir_name):  # loop through items in dir
            file_name =dir_name + os.sep + file
            do_your_thing(file_name)

    elif to_do == "including_subdirectories":
        rootdir = dir_name
        for subdir, dirs, files in os.walk(dir_name):
            for file in files:
                do_your_thing(file)
    else:
        print("ERROR IN 'to_do' variable")

   
if __name__ == "__main__":
    main()


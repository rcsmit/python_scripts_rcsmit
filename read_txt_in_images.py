################################################################
#
#     Recognize text in all image files in a certain directory
#     And write it to seperate or one textfile(s) or a SQLite3 database
#
#################################################################

# Make sure you installed Pytesseract : https://stackoverflow.com/questions/50951955/pytesseract-tesseractnotfound-error-tesseract-is-not-installed-or-its-not-i

# TODO : clear confusion betweend dir_name and rootdir
#        add creation/modification date/time as field
#        if there is an error, you have to start all over again with reading the directories


# Import libraries
from PIL import Image
import pytesseract
# from pdf2image import convert_from_path
import os
import time
import sqlite3 as sl
import pandas as pd


def convert_txt_to_ocr(file_name):
    """Really recognize the text in the image to text
    Args:
        file_name (string): the filename

    Returns:
        text: the text in the image
    """
    print(f"Converting {file_name}")
    pytesseract.pytesseract.tesseract_cmd = (
        r"C:\Program Files\Tesseract-OCR\tesseract.exe"
    )
    try:
        text = str(((pytesseract.image_to_string(Image.open(file_name)))))
    except:
        print (f"Error reading {file_name}")
        text = ""
    return text


def txt_to_ocr(dir_name, item, extensionsToCheck):
    """See if the file is an image, check there is text in the image and save/append the text to a file"""
    for e in extensionsToCheck:
        if item.endswith(e):
            file_name = dir_name + os.sep + item
            print(f"Processing {file_name}")
            text = convert_txt_to_ocr(file_name)
            if len(text) > 0 :
                return text
            else:
                print(f"No text found in {file_name}")


def save_text(text, filename, modus, dir_name, rootdir):
    """Save/append the text to a file"""
    print(f"Saving {filename}")

    if modus == "new":
        filename = filename.replace(".PNG", "_PNG")
        filename = filename.replace(".png", "_png")
        filename = filename.replace(".jpg", "_jpg")
        filename = filename.replace(".jpeg", "_jpeg")
        filename = filename.replace(".JPG", "_JPG")
        filename_txt = filename + ".txt"

        with open(filename_txt, "w") as f:
            print(f"Saving {filename}")
            f.write(text)
    elif modus == "append":
        file_to_save = rootdir + os.sep + " text_in_images.txt"
        with open(file_to_save, "a") as f:
            print(f"Adding {filename} to textfile")
            # f.write('\n')
            # f.write('\n')
            f.write(f"\n\n=== {dir_name} \ {filename} ===\n")
            # f.write('\n')
            f.write(text)
    else:
        print("ERROR IN ' modus'")

def insert_text_to_database( con, directory, filename, text):
    """Insert the text in the database
    """    
    print(f"Writing {filename} to database")
    sql = 'INSERT INTO txt_from_images( directory, filename, text_in_image) values(?,?, ?)'
    data = [
        (directory, filename,text )  
    ]
    with con:
        con.executemany(sql, data)


def take_action_with_text(dir_name, modus, action, text, file_name,rootdir,con):
    """Save to textfile or to database?
    """    
    if text is not None:
        if action == "save_to_database":
            insert_text_to_database( con, dir_name, file_name, text)
        elif action == "save_to_txt_file":
            save_text(text, file_name, modus, dir_name, rootdir)
        else:
            print ("ERROR in 'action'")

def read_db(keyword):
    """Search the database for a certain keyword
    Should be in a seperate script and made webbased, just added here to show the possibilities after the OCR process

    """    
    # keyword = "vegan"
    if keyword is not None:
        sql_statement = f" SELECT directory, filename, text_in_image FROM txt_from_images where text_in_image LIKE '%{keyword}%'"
    else:

        sql_statement = f" SELECT directory, filename, text_in_image FROM txt_from_images" 
    dir_name = r"C:\Users\rcxsm\Pictures"

    db_name = dir_name + os.sep + "my_test.db"
    con = sl.connect(db_name)

    df = pd.read_sql(sql_statement, con)
    print (df)

    # TODO: nice interface, show also the image as clickable thumbnail


def main():
    ######################################################################
    dir_name = r"C:\Users\rcxsm\Pictures\ocr_test"
    extensionsToCheck = [".jpg", ".JPG", ".jpeg", ".png", ".PNG"]
    modus = "new"  # "append"  # 'new' to place text in seperate textfiles, ' append' to put all text in one file
    to_do = "including_subdirectories"#  "single_directory" #"including_subdirectories"
    action = "save_to_database" #"save_to_txt_file" #"save_to_database"
    #######################################################################
    if action == "save_to_database":
        db_name = dir_name + os.sep + "my_test.db"
        con = sl.connect(db_name)
        try:
            with con:
                con.execute("""
                    CREATE TABLE txt_from_images (
                        id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
                        directory TEXT,
                        filename TEXT,
                        text_in_image TEXT
                    );
                """)
        except: 
            print ("Table exists already")
    else:
        con = None
    s1 = int(time.time())

    if to_do == "single_directory":
        rootdir = dir_name
        print(f"Browsing {dir_name}")
        lengte = len(os.listdir(dir_name))
        n = 1
        os.chdir(dir_name)  # change directory from working dir to dir with files

        for file in os.listdir(dir_name):  # loop through items in dir
            print(f"{n}/{lengte}")
            text = txt_to_ocr(dir_name, file, extensionsToCheck)
            take_action_with_text(dir_name, modus, action, text, file,rootdir,con)
            n = n + 1


    elif to_do == "including_subdirectories":
        rootdir = dir_name
        for subdir, dirs, files in os.walk(dir_name):
            for file in files:
                print(f"{subdir =}")
                print(f"{file =}")
                text = txt_to_ocr(subdir, file, extensionsToCheck)
                take_action_with_text(subdir, modus, action, text, file,rootdir, con)
    else:
        print("ERROR IN 'to_do' variable")

    s2 = int(time.time())
    s2x = s2 - s1
    print("Downloading  took " + str(s2x) + " seconds ....")

    if action == "save_to_database":
        # show all the records
        with con:
            data = con.execute("SELECT * FROM txt_from_images")
            for row in data:
                print(row)

        # show the results containing a certain keyword
        read_db('vegan')


main()

#read_db(None)

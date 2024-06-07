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
        text = (f"Error reading {file_name}")
        #text = ""
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
    #print(f"Saving {filename}")

    if modus == "new":
        filename = filename.replace(".PNG", "_PNG")
        filename = filename.replace(".png", "_png")
        filename = filename.replace(".jpg", "_jpg")
        filename = filename.replace(".jpeg", "_jpeg")
        filename = filename.replace(".JPG", "_JPG")
        filename_txt = filename + ".txt"

        with open(filename_txt, "w") as f:
            #print(f"Saving {filename}")
            f.write(text)
    elif modus == "append":
        file_to_save = rootdir + os.sep + " text_in_images.txt"
        with open(file_to_save, "a") as f:
            print(f"Adding {filename} to textfile")
            f.write(f"\n\n=== {dir_name} \ {filename} ===\n")
            f.write(text)
    else:
        print("ERROR IN 'modus'")

def insert_text_to_database( con, directory, filename, text):
    """Insert the text in the database
    """    
    

    #TODO: see if file is already in database
    sql_test = "SELECT count(*) FROM  txt_from_images WHERE  directory=? AND filename=? AND text_in_image=?"
    data_test = (directory, filename,text)
    
    if con.execute(sql_test, data_test).fetchone()[0] == 0:
        print(f"Writing {filename} to database")
        sql = 'INSERT INTO txt_from_images( directory, filename, text_in_image) values(?,?, ?)'
        data = [
            (directory, filename,text )  
        ]
        with con:
            con.executemany(sql, data)
        
    else:
        print(f"record exists already for {directory}\{filename}")


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


def convert_pdf(dir_name):
    """Convert PDF to image. Very slow, it takes 70 seconds for a file of 5 pages.
        Has to be implemented further in this script.  UNDER CONSTRUCTION
    Args:
        dir_name (_type_): _description_
    """     
    pages = convert_from_path(r"C:\Users\rcxsm\Pictures\ocr_test\deloitte\reactie-op-brief-deloitte.pdf", 500,  poppler_path=r"C:\Program Files\poppler\Library\bin")
    print ("Pages converted")
    for x, page in enumerate(pages):
        print (f"Saving page {x}/{len(pages)}")
        page.save(f'C:\\Users\\rcxsm\\Pictures\\ocr_test\\deloitte\\deloitte_{x}.jpg', 'JPEG')

def delete_records_from_db(db_dir, dir, file_name_db ):
    sql_statement = f"DELETE FROM txt_from_images WHERE directory = '{dir}'"
    db_name = db_dir + os.sep + file_name_db 
    con = sl.connect(db_name)

    cur = con.cursor()
    print(f" PROCESSING {sql_statement}")

    cur.execute(sql_statement)
    con.commit()
    print (f" DONE {sql_statement}")

def read_incl_subdir(action, dir_name, extensionsToCheck, file_name_contains, modus, con):
    rootdir = dir_name
    for subdir, dirs, files in os.walk(dir_name):
        f = len(files)
        print (subdir)
        for idx, file in enumerate(files):
        
            if file_name_contains != None:
                print (file)
                if file_name_contains in file:
                    print(f"{subdir =}")
                    print(f"{idx}/{f} - {file =}")
                    text = txt_to_ocr(subdir, file, extensionsToCheck)
                    take_action_with_text(subdir, modus, action, text, file,rootdir, con)

def read_single_dir(action, dir_name, extensionsToCheck, file_name_contains, modus, con):
    print ("read single dir")
    rootdir = dir_name
    print(f"Browsing {dir_name}")
    lengte = len(os.listdir(dir_name))
    n = 1
    os.chdir(dir_name)  # change directory from working dir to dir with files

    for file in os.listdir(dir_name):  # loop through items in dir
        print (file)
        if file_name_contains != None:
            if file_name_contains in file:
                print(f"{n}/{lengte}")
                text = txt_to_ocr(dir_name, file, extensionsToCheck)
                take_action_with_text(dir_name, modus, action, text, file,rootdir,con)
                n = n + 1
        else:
            print(f"{n}/{lengte}")
            text = txt_to_ocr(dir_name, file, extensionsToCheck)
            take_action_with_text(dir_name, modus, action, text, file,rootdir,con)
            n = n + 1




def do_action(action, dir_name, dir_name_db,  file_name_db, extensionsToCheck, file_name_contains, modus, to_do):
    if action == "delete_dir_from_db":
        delete_records_from_db(dir_name_db, dir_name, file_name_db )
    elif action == "save_to_database":
        db_name = dir_name_db + os.sep +  file_name_db 
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
        read_single_dir(action, dir_name, extensionsToCheck, file_name_contains, modus, con)

    elif to_do == "including_subdirectories":
        read_incl_subdir(action, dir_name, extensionsToCheck,file_name_contains, modus, con)
    else:
        print("ERROR IN 'to_do' variable")

    s2 = int(time.time())
    s2x = s2 - s1
    print("Downloading  took " + str(s2x) + " seconds ....")

def main():
    ######################################################################
    #dir_name = r"C:\Users\rcxsm\Pictures\ocr_test"
    #dir_name = r"C:\Users\rcxsm\Pictures\div\mijn autos\b"
    #dir_name = r"C:\Users\rcxsm\Pictures\div\mijn autos\b\dls\various"
    #dir_name = r"C:\Users\rcxsm\Downloads\Sheetmusic\sheetmusic\gefotografeerd"
    #dir_name_db = r"C:\Users\rcxsm\Downloads\Sheetmusic\sheetmusic\gefotografeerd"
    ################################################################################
    
    action =  "save_to_database" # "save_to_txt_file" #"save_to_database" # "delete_dir_from_db"
    #dir_name = r"C:\Users\rcxsm\Pictures\div\mijn autos\b\dls\tinder2022"
    dir_name = "C:\\Users\\rcxsm\\Pictures\\div\\mijn autos\\b\\dls\\tinder_bumble"
    dir_name_db = "C:\\Users\\rcxsm\\Pictures\\div\\mijn autos\\b\\dls\\tinder_bumble"
    #dir_name_db = r"C:\Users\rcxsm\Pictures\div\mijn autos\b"
    file_name_db = "my_test.db"

    extensionsToCheck = [".jpg", ".JPG", ".jpeg", ".png", ".PNG"]
    modus = "new"  # "append"  # 'new' to place text in seperate textfiles, ' append' to put all text in one file
    to_do =  "single_directory" # "including_subdirectories"#  #"including_subdirectories"
    file_name_contains = None # "Instagram"
    do_action(action, dir_name, dir_name_db, file_name_db, extensionsToCheck,file_name_contains, modus, to_do)

if __name__ == "__main__":
    main()
    

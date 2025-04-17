import sqlite3 as sl
import numpy as np
import io
import os
import pandas as pd
import face_recognition
import json

def adapt_array(arr):
    """
    http://stackoverflow.com/a/31312102/190597 (SoulNibbler)
    """
    out = io.BytesIO()
    np.save(out, arr)
    out.seek(0)
    return sl.Binary(out.read())

def convert_array(text):
    out = io.BytesIO(text)
    out.seek(0)
    return np.load(out)

def convert_JSON_to_list(data):
    return json.loads(data.decode('utf8'))

sl.register_converter("json", convert_JSON_to_list)


# # Converts np.array to TEXT when inserting
# sl.register_adapter(np.ndarray, adapt_array)

# # Converts TEXT to np.array when selecting
# sl.register_converter("face_encoding_in_image", convert_array)

x = np.arange(12).reshape(2,6)
dir_name_db = 'C:\\Users\\rcxsm\\Pictures\\div\\mijn autos\\b\\dls\\'
file_name_db = "face_encodings.db"
db_name = dir_name_db + os.sep +  file_name_db 
con = sl.connect(db_name, detect_types=sl.PARSE_DECLTYPES)
# con = sl.connect(":memory:", detect_types=sl.PARSE_DECLTYPES)
cur = con.cursor()
#cur.execute("DROP TABLE face_encoding_from_images")

try:
    with con:
        con.execute("""
            CREATE TABLE face_encoding_from_images (
                id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
                directory TEXT,
                filename TEXT,
                face_encoding_in_image ARRAY
            );
        """)
except: 
    print ("Table exists already")


print ("Reading known image")
#With this setup, you can simply insert the NumPy array with no change in syntax:
known_image_url = r"C:\Users\rcxsm\Pictures\div\mijn autos\b\dls\2020f\FB_IMG_1601671543561.jpg"
known_image = face_recognition.load_image_file(known_image_url)
# face_encoding_known = face_recognition.face_encodings(known_image)[0]
# print (face_encoding_known.dtype())
# sql_store = "insert into face_encoding_from_images (directory, filename, face_encoding_in_image) values (?,?,?)"
# data_store = ("c:\rene", "test.jpg", face_encoding_known) 
# cur.execute(sql_store, data_store)


#And retrieve the array directly from sqlite as a NumPy array:
print ("Retrieving image)")
# con.execute("SELECT directory, filename, face_encoding_in_image FROM face_encoding_from_images")
# data = cur.fetchone()

# #print(data)
# # [[ 0  1  2  3  4  5]
# #  [ 6  7  8  9 10 11]]
# #print(type(data))
# # <type 'numpy.ndarray'>

sql_statement = "SELECT * FROM face_encoding_from_images"
data = cur.fetchall()
#print (data)

df = pd.read_sql(sql_statement, con)
#print (df)
for i in range(len(df)):
    known_encoding =  np.array(df.iloc[i,3])
    


    unknown_image = r"C:\Users\rcxsm\Pictures\div\mijn autos\b\dls\test\FB_IMG_1601671543561.jpg"
    unknown_image = face_recognition.load_image_file(unknown_image)
    if len (face_recognition.face_encodings(unknown_image))>0:
        unknown_encoding = face_recognition.face_encodings(unknown_image)[0]
        results = face_recognition.compare_faces(
            [known_encoding], unknown_encoding, tolerance=0.6
        )
        print (results)
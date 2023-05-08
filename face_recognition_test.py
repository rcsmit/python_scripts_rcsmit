# https://github.com/ageitgey/face_recognition
# Compares two photos and predicts whether they are the same person

# face_recognition.compare_faces(known_face_encodings, face_encoding_to_check, tolerance=0.6) has been adapted
# added a line to print the score
#      print (f"Distance : {face_distance(known_face_encodings, face_encoding_to_check)}")

import face_recognition
import cv2
import os
import time
import sqlite3 as sl
import numpy as np
import io
import json
import pandas as pd

def show_face_landmarks(url):
    """Shows the landmarks of a given face

    Args:
        url (string):URL or file location of the face
    """
    image = face_recognition.load_image_file(url)
    face_landmarks_list = face_recognition.face_landmarks(image)

    img = cv2.imread(url, cv2.IMREAD_COLOR)
    font = cv2.FONT_HERSHEY_COMPLEX_SMALL
    ih, iw, ic = img.shape

    for face_landmarks in face_landmarks_list:
        for key in face_landmarks:
            todo = face_landmarks[key]
            for i, t in enumerate(todo):
                a = t[0]
                b = t[1]
                cv2.circle(img, (a, b), radius=5, color=(225, 0, 100), thickness=1)
                font = cv2.FONT_HERSHEY_COMPLEX_SMALL
                txt = f"{str(i)}-{key}"
                # cv2.putText(img,txt,(a, b), font, 1, (255,255,255), 1, cv2.LINE_AA)
    cv2.imshow("image", img)
    cv2.waitKey(0)

def get_known_image(known_image):
    """Gets the numpy array of the known face

    Args:
        known_image (string): Filename of the file with the known face
        unknown_image (string): Filename of the file with the unknown face

    Returns:
        Boolean: Whether the unknown face is the same as the known face
    """
    known_image = face_recognition.load_image_file(known_image)
    known_encoding = face_recognition.face_encodings(known_image)[0]
    return known_encoding

def indentify_faces(known_image, unknown_image):
    """Checks if the known face is in the unknown image

    Args:
        known_image (string): Filename of the file with the known face
        unknown_image (string): Filename of the file with the unknown face

    Returns:
        Boolean: Whether the unknown face is the same as the known face
    """
    known_image = face_recognition.load_image_file(known_image)
    unknown_image = face_recognition.load_image_file(unknown_image)

    known_encoding = face_recognition.face_encodings(known_image)[0]
    if len (face_recognition.face_encodings(unknown_image))>0:
        unknown_encoding = face_recognition.face_encodings(unknown_image)[0]
        results = face_recognition.compare_faces(
            [known_encoding], unknown_encoding, tolerance=0.6
        )
    else:
        results = [False] # no faces in the image

    return results


def indentify_faces_with_known_encoding(known_encoding, unknown_image):
    """Checks if the known face is in the unknown image

    Args:
        known_image (string): Filename of the file with the known face
        unknown_image (string): Filename of the file with the unknown face

    Returns:
        Boolean: Whether the unknown face is the same as the known face
    """
    unknown_image = face_recognition.load_image_file(unknown_image)

    if len (face_recognition.face_encodings(unknown_image))>0:
        unknown_encoding = face_recognition.face_encodings(unknown_image)[0]
        results = face_recognition.compare_faces(
            [known_encoding], unknown_encoding, tolerance=0.6
        )
    else:
        results = [False] # no faces in the image

    return results

def show_distance(known_image, unknown_image):
    #
    """Load a test image and get the distance to the known image.

    Args:
        known_image (str): filename of the known image
        unknown_image (str): filename of the unknown image to test

    Returns:
        float: distance to test image. 0 is 100% equal, 1 is unequal
    """
    image_known = face_recognition.load_image_file(known_image)
    image_known_encoding = [face_recognition.face_encodings(image_known)[0]]

    # Load a test image and get encondings for it
    image_to_test = face_recognition.load_image_file(unknown_image)
    image_to_test_encoding = face_recognition.face_encodings(image_to_test)[0]

    a = face_recognition.face_distance(image_known_encoding, image_to_test_encoding)
    return a[0]

def index_incl_subdir(dir_name):
    dir_name_db = r"C:\Users\rcxsm\Pictures\div\mijn autos\b\dls"
    file_name_db = "face_encodings.db"
    db_name = dir_name_db + os.sep +  file_name_db 
    con = sl.connect(db_name, detect_types=sl.PARSE_DECLTYPES)
    #con = sl.connect(db_name,detect_types=sqlite3.PARSE_COLNAMES)
    #con = sqlite3.connect(":memory:", )
    cur = con.cursor()
    cur.execute("DROP TABLE face_encoding_from_images")
    try:
        with con:
            con.execute("""
                CREATE TABLE face_encoding_from_images (
                    id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
                    directory TEXT,
                    filename TEXT,
                    face_encoding_in_image json
                );
            """)
    except: 
        print ("Table exists already")
    #sl.register_adapter(np.ndarray, adapt_array)

    sl.register_adapter(list, adapt_list_to_JSON)
    sl.register_converter("json", convert_JSON_to_list)
  
    extensionsToCheck = [".jpg", ".JPG", ".jpeg", ".png", ".PNG"]
    for subdir, dirs, files in os.walk(dir_name):
        f = len(files)
        for idx, file in enumerate(files):
            print(f"{subdir =}")
            print(f"{idx}/{f} - {file =}")
            unknown_image = subdir + os.sep + file


            unknown_image_x=face_recognition.load_image_file(unknown_image)
            if len (face_recognition.face_encodings(unknown_image_x))>0:
                face_encoding_in_image = face_recognition.face_encodings(unknown_image_x)[0]
                print (face_encoding_in_image)
                face_encoding_in_image_as_list = face_encoding_in_image.tolist()
                print (face_encoding_in_image_as_list)
            else:
                print (f"No face found in {file}")

            if face_encoding_in_image is not None:

                sql = "INSERT INTO face_encoding_from_images (directory, filename, face_encoding_in_image) values (?,?,?)"
                data = (subdir, file, face_encoding_in_image_as_list)
                with con:
                    con.execute(sql , data)
                    print (f"Inserted {file}")
            
def check_if_image_is_in_database(unknown_image):
    unknown_image = face_recognition.load_image_file(unknown_image)
  
    sl.register_converter("json", convert_JSON_to_list)

    dir_name_db = 'C:\\Users\\rcxsm\\Pictures\\div\\'
    file_name_db = "face_encodings.db"
    db_name = dir_name_db + os.sep +  file_name_db 
    con = sl.connect(db_name, detect_types=sl.PARSE_DECLTYPES)
    sql_statement = "SELECT * FROM face_encoding_from_images"
    df = pd.read_sql(sql_statement, con)
    for i in range(len(df)):
        known_encoding =  np.array(df.iloc[i,3])
        if len (face_recognition.face_encodings(unknown_image))>0:
            unknown_encoding = face_recognition.face_encodings(unknown_image)[0]
            results = face_recognition.compare_faces(
                [known_encoding], unknown_encoding, tolerance=0.6
            )
            if results[0] == True:
                print ("FOUND")
                print ("ID")
                print (df.iloc[i,0])
                print ("subdir")
                print (df.iloc[i,1])
                print ("filename")
                print (df.iloc[i,2])
                return True
    return False
            
def adapt_list_to_JSON(lst):
    return json.dumps(lst).encode('utf8')

def convert_JSON_to_list(data):
    return json.loads(data.decode('utf8'))


def read_incl_subdir(known_image, test_dir, target_dir):
    """Reads the file, checks if the person is the same as on the known image
       and in that case move the file to the target directory

    Args:
        known_image (str): The file with the known face
        test_dir (str): The directory to check
        target_dir (str): The target directory
    """
    known_encoding = get_known_image(known_image)
    extensionsToCheck = [".jpg", ".JPG", ".jpeg", ".png", ".PNG"]
    for subdir, dirs, files in os.walk(test_dir):
        f = len(files)
        for idx, file in enumerate(files):

            for e in extensionsToCheck:
                if file.endswith(e):
                    print(f"{idx+1}/{f} - {subdir}/{file =}")
                    unknown_image = subdir + os.sep + file
                    #try:
                    result = indentify_faces_with_known_encoding(known_encoding, unknown_image)
                    print (result)
                    if result[0] == True:
                        print(f"Moving {file}")
                        target_file_name = target_dir + os.sep + file
                        print(target_file_name)

                        os.replace(unknown_image, target_file_name)

                    else:
                        print("Not the same")
                    #   print(f"error with {file}")


def main():
    s1 = int(time.time())
    # known_image = r"C:\Users\rcxsm\Downloads\Gal_Gadot_by_Gage_Skidmore_4_600.jpg"
    # test_dir = r"C:\Users\rcxsm\Pictures\div\galtest"
    # target_dir = r"C:\Users\rcxsm\Pictures\div\\galtarget"
    # result = indentify_faces(known_image, unknown_image)
    
    # print (result)
    known_image = (
        r"C:\Users\rcxsm\Downloads\known.jpg"
    )
    unknown_image = r"C:\Users\rcxsm\Downloads\unknown.jpg"
  
    mode = "index_subdirs"
    mode = "check_if_in_database"
    if mode == "show_distance":

        show_face_landmarks(known_image)
        show_face_landmarks(unknown_image)
        distance = show_distance(known_image, unknown_image)
        result = indentify_faces(known_image, unknown_image)

        print(f"Distance: {distance} -  {result}")
    elif mode == "look_for_my_friend":
        known_image = r"C:\Users\rcxsm\Pictures\div\known.jpg"
        target_dir = r"C:\Users\rcxsm\Pictures\div\target_dir\"
        test_dir_ = [
         
            r"C:\Users\rcxsm\Pictures\div\test_dir",
        ]
        for test_dir in test_dir_:
            read_incl_subdir(known_image, test_dir, target_dir)
    elif mode == "index_subdirs":
        test_dir_ = [
         
            r"C:\Users\rcxsm\Pictures\div\test_dir",
          
        for test_dir in test_dir_:
            index_incl_subdir(test_dir)
    elif mode == "check_if_in_database":
        image_to_check = r"C:\Users\rcxsm\Pictures\div\check_whether_in_database.jpg"
       
        result = check_if_image_is_in_database(image_to_check)
        if result == True:
            print ("I move it")
        else:
            print ("I dont move it")
        
    else:
        print("ERROR in /mode/")
    s2 = int(time.time())
    s2x = s2 - s1
    print("Downloading  took " + str(s2x) + " seconds ....")



main()

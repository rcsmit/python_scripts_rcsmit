import face_recognition
import cv2
import os


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
                cv2.putText(img,txt,(a, b), font, 1, (255,255,255), 1, cv2.LINE_AA)
    cv2.imshow("image", img)
    cv2.waitKey(0)


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
    unknown_encoding = face_recognition.face_encodings(unknown_image)[0]
    results = face_recognition.compare_faces(
        [known_encoding], unknown_encoding, tolerance=0.6
    )
    return results


def read_incl_subdir(known_image, test_dir, target_dir):
    """Reads the file, checks if the person is the same as on the known image
       and in that case move the file to the target directory

    Args:
        known_image (str): The file with the known face
        test_dir (str): The directory to check
        target_dir (str): The target directory
    """

    extensionsToCheck = [".jpg", ".JPG", ".jpeg", ".png", ".PNG"]
    for subdir, dirs, files in os.walk(test_dir):
        f = len(files)
        for idx, file in enumerate(files):

            for e in extensionsToCheck:
                if file.endswith(e):
                    print(f"{idx+1}/{f} - {subdir}/{file =}")
                    unknown_image = test_dir + os.sep + file
                    try:
                        result = indentify_faces(known_image, unknown_image)
                        if result[0] == True:
                            print(f"Moving {file}")
                            target_file_name = target_dir + os.sep + file
                            print(target_file_name)

                            os.replace(unknown_image, target_file_name)

                        else:
                            print("Not the same")
                    except:
                        print(f"error with {file}")


def main():
    known_image = r"C:\Users\rcxsm\Downloads\Gal_Gadot_by_Gage_Skidmore_4_600.jpg"
    test_dir = r"C:\Users\rcxsm\Pictures\div\galtest"
    target_dir = r"C:\Users\rcxsm\Pictures\div\\galtarget"

    show_face_landmarks(known_image)
    read_incl_subdir(known_image, test_dir, target_dir)


main()

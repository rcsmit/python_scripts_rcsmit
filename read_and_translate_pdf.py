
# "C:\Users\rcxsm\Documents\python_scripts\code_behorende_bij_boeken\realpython\materials-master\creating-and-modifying-pdfs\source_code\01-extracting-text-from-a-pdf.py"
# https://www.geeksforgeeks.org/extract-text-from-pdf-file-using-python/
# ---------------
# Open a PDF File
# ---------------

from PyPDF2 import PdfReader
from pathlib import Path
from googletrans import Translator
# # Import libraries
# from PIL import Image
# import pytesseract
# from pdf2image import convert_from_path
# import os
# import time
# import sqlite3 as sl
# import pandas as pd

# def convert_txt_to_ocr(file_name):
#     """Really recognize the text in the image to text
#     Args:
#         file_name (string): the filename

#     Returns:
#         text: the text in the image
#     """
#     print(f"Converting {file_name}")
#     pytesseract.pytesseract.tesseract_cmd = (
#         r"C:\Program Files\Tesseract-OCR\tesseract.exe"
#     )
#     try:
#         text = str(((pytesseract.image_to_string(Image.open(file_name)))))
#     except:
#         text = (f"Error reading {file_name}")
#         #text = ""
#     return text


# def convert_pdf(dir_name):
#     """Convert PDF to image. Very slow, it takes 70 seconds for a file of 5 pages.
#         Has to be implemented further in this script.  UNDER CONSTRUCTION
#     Args:
#         dir_name (_type_): _description_
#     """     
#     pages = convert_from_path(r"C:\Users\rcxsm\Pictures\ocr_test\deloitte\reactie-op-brief-deloitte.pdf", 500,  poppler_path=r"C:\Program Files\poppler\Library\bin")
#     print ("Pages converted")
#     for x, page in enumerate(pages):
#         print (f"Saving page {x}/{len(pages)}")
#         page.save(f'C:\\Users\\rcxsm\\Pictures\\ocr_test\\deloitte\\deloitte_{x}.jpg', 'JPEG')


def read_pdf(pdf_path):
    # You might need to change this to match the path on your computer
    # creating a pdf reader object
    reader = PdfReader(pdf_path)
    
    # printing number of pages in pdf file
    print(len(reader.pages))
    
    # getting a specific page from the pdf file
    #page = reader.pages[0]
    text = ""
    for page in reader.pages:
        # extracting text from page
        text += page.extract_text()
    print(text)
    return text


def translate(text):
    print("translating")
    translator = Translator()
    vertaalde_tekst = translator.translate(text,  dest='nl').text
    return vertaalde_tekst

def main():
    pdf_path = r"C:\Users\rcxsm\Downloads\How-to-jam-Center-Of-Gravity.pdf"

    #pdf_path=r"C:\Users\rcxsm\Downloads\vacansoleil\maintenance schatberg sept2023.pdf"
    text = read_pdf(pdf_path)

    print (text)
    print (translate(text))

main()



# def main():
#     ######################################################################
#     #dir_name = r"C:\Users\rcxsm\Pictures\ocr_test"
#     #dir_name = r"C:\Users\rcxsm\Pictures\div\mijn autos\b"
#     #dir_name = r"C:\Users\rcxsm\Pictures\div\mijn autos\b\dls\various"
#     #dir_name = r"C:\Users\rcxsm\Downloads\Sheetmusic\sheetmusic\gefotografeerd"
#     #dir_name_db = r"C:\Users\rcxsm\Downloads\Sheetmusic\sheetmusic\gefotografeerd"
#     ################################################################################
    
#     action = "save_to_database" #"save_to_txt_file" #"save_to_database" # "delete_dir_from_db"
#     dir_name = r"C:\Users\rcxsm\Pictures\div\mijn autos\b\dls\tinder2022"
#     dir_name_db = r"C:\Users\rcxsm\Pictures\div\mijn autos\b"
#     file_name_db = "my_test.db"

#     extensionsToCheck = [".jpg", ".JPG", ".jpeg", ".png", ".PNG"]
#     modus = "new"  # "append"  # 'new' to place text in seperate textfiles, ' append' to put all text in one file
#     to_do = "including_subdirectories"#  "single_directory" #"including_subdirectories"
   
#     do_action(action, dir_name, dir_name_db, file_name_db, extensionsToCheck, modus, to_do)


# # (
# #     Path.home()
# #     / "creating-and-modifying-pdfs"
# #     / "practice_files"
# #     / "Pride_and_Prejudice.pdf"
# # )

# pdf = PdfReader(str(pdf_path))

# # print(pdf.getNumPages())

# # print(pdf.documentInfo)

# # print(pdf.documentInfo.title)


# # ---------------------------
# # Extracting Text From a Page
# # ---------------------------

# first_page = pdf.getPage(0)

# print(type(first_page))

# print(first_page.extractText())

# for page in pdf.pages:
#     print(page.extractText())


# # -----------------------
# # Putting It All Together
# # -----------------------

# from pathlib import Path  # noqa
# from PyPDF2 import PdfFileReader  # noqa

# # Change the path below to the correct path for your computer.
# pdf_path = (
#     Path.home()
#     / "creating-and-modifying-pdfs"
#     / "practice-files"
#     / "Pride_and_Prejudice.pdf"
# )

# pdf_reader = PdfFileReader(str(pdf_path))
# output_file_path = Path.home() / "Pride_and_Prejudice.txt"

# with output_file_path.open(mode="w") as output_file:
#     title = pdf_reader.documentInfo.title
#     num_pages = pdf_reader.getNumPages()
#     output_file.write(f"{title}\\nNumber of pages: {num_pages}\\n\\n")

#     for page in pdf_reader.pages:
#         text = page.extractText()
#         output_file.write(text)

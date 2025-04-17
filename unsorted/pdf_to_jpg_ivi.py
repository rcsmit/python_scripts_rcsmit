

# Import libraries
from PIL import Image
import pytesseract
from pdf2image import convert_from_path
import os
import time
import sqlite3 as sl
import pandas as pd

def convert_pdf(file_name):
    filename_pdf = file_name.replace(".PDF", "")
    pages = convert_from_path(file_name, 500,  poppler_path=r"C:\Program Files\poppler\Library\bin")
    print ("Pages converted")
    for x, page in enumerate(pages):
        print (f"Saving page {x+1}/{len(pages)}")
        page.save(f'{filename_pdf}_{x+1}.jpg', 'JPEG')

def main():
    # files = [r"C:\Users\rcxsm\Downloads\insurance_decl_ivi_2022.pdf", r"C:\Users\rcxsm\Downloads\Covid 2.pdf", r"C:\Users\rcxsm\Downloads\Covid 1.jpeg.pdf",
    #          r"C:\Users\rcxsm\Downloads\Thai visa - Ivi insurance - April 2022.pdf"]
    files = [r"C:\Users\rcxsm\Downloads\CP potvrzení.PDF"]
    for f in files:
        convert_pdf(f)

main()


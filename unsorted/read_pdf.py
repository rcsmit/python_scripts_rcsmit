# https://www.geeksforgeeks.org/python-reading-contents-of-pdf-using-ocr-optical-character-recognition/


# Import libraries
# from PIL import Image
# import pytesseract
# import sys
# from pdf2image import convert_from_path
# import os
from PyPDF2 import PdfReader
import re
import pandas as pd

def pdf_to_images():
    # Path of the pdf
    PDF_file = "C:/Users/rcxsm/Downloads/besluit-en-openbaar-gemaakte-documenten-wob-verzoek-repatriering-nederlanders-uit-marokko.pdf"
    PDF_file = "C:/Users/rcxsm/Downloads/Bijlage%20B%20-%20Wob-deelbesluit%20Vaccinaties%20en%20medicatie%20oktober%202020.pdf"
    PDF_file = r"C:\Users\rcxsm\Downloads\_OceanofPDF.com_Unreasonable_Hospitality_-_Will_Guidara.pdf"
    '''
    Part #1 : Converting PDF to images
    '''

    # Store all the pages of the PDF in a variable
    pages = convert_from_path(PDF_file, 500, poppler_path = r"C:\Program Files\poppler\Library\bin")
    print (len(pages))
    # Counter to store images of each page of PDF to image
    image_counter = 1, 

    # Iterate through all the pages stored above
    for page in pages:
        print (image_counter)
        # Declaring filename for each page of PDF as JPG
        # For each page, filename will be:
        # PDF page 1 -> page_1.jpg
        # PDF page 2 -> page_2.jpg
        # PDF page 3 -> page_3.jpg
        # ....
        # PDF page n -> page_n.jpg
        filename = "page_"+str(image_counter)+".jpg"
        
        # Save the image of the page in system
        page.save(filename, 'JPEG')

        # Increment the counter to update filename
        image_counter = image_counter + 1

def ocr_text_from_images():
    '''
    Part #2 - Recognizing text from the images using OCR
    '''

    # Variable to get count of total number of pages
    filelimit =  10 # image_counter-1

    # Creating a text file to write the output
    outfile = "out_text.txt"

    # Open the file in append mode so that
    # All contents of all images are added to the same file
    f = open(outfile, "a")

    # Iterate from 1 to total number of pages
    for i in range(1, filelimit + 1):

        # Set filename to recognize text from
        # Again, these files will be:
        # page_1.jpg
        # page_2.jpg
        # ....
        # page_n.jpg
        filename = "page_"+str(i)+".jpg"
            
        # Recognize the text as string in image using pytesserct
        text = str(((pytesseract.image_to_string(Image.open(filename)))))

        # The recognized text is stored in variable text
        # Any string processing may be applied on text
        # Here, basic formatting has been done:
        # In many PDFs, at line ending, if a word can't
        # be written fully, a 'hyphen' is added.
        # The rest of the word is written in the next line
        # Eg: This is a sample text this word here GeeksF-
        # orGeeks is half on first line, remaining on next.
        # To remove this, we replace every '-\n' to ''.
        text = text.replace('-\n', '')    

        # Finally, write the processed text to the file.
        f.write(text)

    # Close the file after writing all the text.
    f.close()

def read_directly_from_pdf():
    # read a file 
    # inspired by https://x.com/Transparangst/status/1906717209423974689
    
    # Install PyPDF2 if not already installed
    # pip install PyPDF2

    # Path to the PDF file
    
    pdf_path = "C:/Users/rcxsm/Downloads/vac_med_okt_2020.pdf"
    
    # Create a PDF reader object
    reader = PdfReader(pdf_path)
    all_text = ""
    # Extract text from each page
    number_of_pages = len(reader.pages)
    for i,page in enumerate(reader.pages):
        
        text = page.extract_text()
        text = re.sub(r'(\n\d{6})', r'\1#', text)
        
        for t in ["Reeds Openbaar", "Deels Openbaar", "Niet Openbaar", "Openbaar"]:
            text = text.replace(t, f'#{t}#')
            text = text.replace('#Deels #Openbaar##','#Deels Openbaar#')
            text = text.replace('#Reeds #Openbaar##','#Reeds Openbaar#')
            text = text.replace('#Niet #Openbaar##','#Niet Openbaar#')
            
        text = text.replace("# ", "#")
        text = text.replace("; 10.","#10.")
        text = text.replace("; 11.","#11.")
        text = text.replace("; buiten verzoek","#buiten verzoek")
        print (f"Reading page {i}/{number_of_pages}")
        all_text +="\n"+text
        # if i>2:
        #     test purposes
        #     break
    # Split text into rows and columns using '#' as a separator
    rows = [line.split('#') for line in all_text.splitlines()]
    
    # Convert to DataFrame
    df = pd.DataFrame(rows)
    print(df)
    
    # Iterate through rows and check columns 3 to 8 for "10.2.a"
    for i in ["a","b","c","d","e","f","g"]:
        df[f"101{i}"] = df.iloc[:, 3:9].apply(lambda row: f"10.1.{i}" in row.values, axis=1)    
        df[f"102{i}"] = df.iloc[:, 3:9].apply(lambda row: f"10.2.{i}" in row.values, axis=1)    
    
    df["BuitenVerzoek"] = df.iloc[:, 3:9].apply(lambda row: "buiten verzoek" in row.values, axis=1)
    df["111concept"] = df.iloc[:, 3:9].apply(lambda row: "11.1, concept" in row.values, axis=1)

    df.to_csv("output.csv", index=False)
    df.to_excel("output.xlsx", index=False)

def main():
    read_directly_from_pdf()

if __name__ == "__main__":
    main()  
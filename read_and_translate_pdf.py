
# "C:\Users\rcxsm\Documents\python_scripts\code_behorende_bij_boeken\realpython\materials-master\creating-and-modifying-pdfs\source_code\01-extracting-text-from-a-pdf.py"
# https://www.geeksforgeeks.org/extract-text-from-pdf-file-using-python/
# ---------------
# Open a PDF File
# ---------------

from PyPDF2 import PdfReader
from pathlib import Path
from googletrans import Translator

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
    translator = Translator()
    vertaalde_tekst = translator.translate(text,  dest='nl').text

    return vertaalde_tekst

def main():
    
    pdf_path = r"C:\Users\rcxsm\Downloads\20230501 - #45 - The month that was.pdf"
    text = read_pdf(pdf_path)
    print (translate(text))

main()
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

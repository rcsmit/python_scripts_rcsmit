# Reads image from clipboard
# Applies OCR
# Pasts text to clipboard

#from itsdangerous import NoneAlgorithm
import win32clipboard  # part of pywin32
#from PIL import Image
import pytesseract
from PIL import ImageGrab

image = ImageGrab.grabclipboard()

pytesseract.pytesseract.tesseract_cmd = (
    r"C:\Program Files\Tesseract-OCR\tesseract.exe"
)
if image is not None:
    text = str(pytesseract.image_to_string(image))
    
    if text== None or text == "":
        print ("No text in image")
    else:
        print (text)
        win32clipboard.OpenClipboard()
        win32clipboard.EmptyClipboard()
        win32clipboard.SetClipboardText( text, win32clipboard.CF_TEXT )
        win32clipboard.CloseClipboard()
        print ("pasted")
else:
    print ("No image on clipboard")
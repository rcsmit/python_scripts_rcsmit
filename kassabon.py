# Recognize the text on a cash register receipt of a supermarkt and put the info in a dataframe
# With the help of ChatGPT
# https://chat.openai.com/share/b78b8a63-fb6e-41c2-a874-3c682b61578f

import pytesseract
from PIL import Image

import re
import pandas as pd


OCR=True
if OCR:
    # Provide the path to the Tesseract executable
    pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
   
    # Provide the path to your image
    #image_path = r"C:\Users\rcxsm\Documents\python_scripts\python_scripts_rcsmit\input\kassabon_lidl_30_05_2023.jpg"
    image_path = r"C:\Users\rcxsm\Documents\python_scripts\python_scripts_rcsmit\input\kassabon_jumbo_31_05_2023.jpg"
    # Open the image using PIL (Python Imaging Library)
    image = Image.open(image_path)

    # Convert the image to grayscale (optional but often improves accuracy)
    grayscale_image = image.convert("L")

    # Perform OCR using Tesseract
    recognized_text = pytesseract.image_to_string(grayscale_image)
    print (recognized_text)
else:
    recognized_text = "Vegan rulgehakt 1,89 B\nActieprijs -0,40\nChampignons 1,99 B\nWoksauzen 1,19 B\nACE multivitamine 3x1,49 4,47 B\nLosse fles PET groot 3x 0,25 0,75 A\nPastasaus-Basilicum 2x 1,59 3,18 B\nBananen  1,50 B\n1,008 kg x 1,49 EUR"

# Split the recognized text into different lines
lines = recognized_text.splitlines()


# Define the regular expression pattern
pattern = r'^(.*?)\s*(?:(\d+)\s*x)?\s*(-?[\d,]+(?:\.\d{2})?)\s*([\d,]+(?:\.\d{2})?)?\s*(\w+)$'

# https://techlabs-aachen.medium.com/ocr-for-extracting-information-from-supermarket-receipts-96bec1cfabfd
word_pattern  = (r"\b[A-Z.]+ [A-Z./]+ [A-Z.]+\b|\b[A-Z.]+ [0-9,]* [A-Z.%]*\b|\b[A-Z.!]+ [A-Z.]+\b|\b[A-Z]+\b")
digit_pattern = (r"\d{1,2},\d{2}[ ][AB]")
# Initialize an empty list to store the extracted data
data = []

# Process each line
for line in lines:
    if "EUR" in line:
        continue  # Ignore the line

    # Use regular expression to extract information
    match = re.match(pattern, line)
    # Check if the pattern matched successfully
    if match:
        # Extract the values using group() method
        description = match.group(1).strip()
        amount = match.group(2) or '1'  # Assign default value of 1 if no amount is specified
        price = match.group(3).replace(',', '.') if match.group(3) else ''
        total_price = match.group(4).replace(',', '.') if match.group(4) else price
        category = match.group(5).strip()

        # Append the extracted data to the list
        data.append({
            'Description': description,
            'Amount': amount,
            'Price': price,
            'Total Price': total_price,
            'Category': category
        })
    else:
        print (f"No match for {line}")

# Create a DataFrame
df = pd.DataFrame(data)

# Print the DataFrame
print(df)
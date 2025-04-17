import requests
import os
import re

#url = r"C:\Users\rcxsm\Documents\python_scripts\index_weirdwonderfulai.html"
url = r"C:\Users\rcxsm\Documents\python_scripts\artists.html"



def save_images(good_links):

    """Save the images in the list

    """    
    save_directory = r"C:\Users\rcxsm\Downloads\AI images\weirdwonderfulaiart\styles"
    failed = []
    for i,image_link in enumerate(good_links):
        print (f"{image_link} [{i+1}/{len(good_links)}]")
        image_url = image_link
        image_name = image_link.split("/")[-1]
        save_path = os.path.join(save_directory, image_name)

        if os.path.exists(save_path):
            print(f"Image {image_name} already exists. Skipping to the next image.")
            continue

        try:
            image_data = requests.get(image_url).content
            with open(save_path, "wb") as f:
                f.write(image_data)
            print(f"Image {image_name} saved successfully.")
        except Exception as e:
            print(f"Failed to save {image_name}. Error: {e}")
            failed.append(image_link)
    print("FAILED")
    print (failed)

def take_from_internet():
    response = requests.get(url)
    response.raise_for_status()

    image_links = response.text.split('\n')

    save_images(image_links)

def take_from_local():
    file_path = url

    # Read the file content
    with open(file_path, "r") as file:
        content = file.read()
 
    # Find all links using regular expressions
    pattern = r"http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+"
    links = re.findall(pattern, content)
   
    # Check if links end with '.jpg'
    good_links = [link for link in links if (link.endswith('.jpg') and  ("x" not in link)) ]
    print(good_links)
    # Print the found links
    save_images(good_links)


take_from_local()





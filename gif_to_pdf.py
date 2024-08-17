from PIL import (
    Image,
)  
# Making ONE pdf from a list of images
# based on https://stackoverflow.com/a/47283224/4173718 CC BY 4.0
# install by > python3 -m pip install --upgrade Pillow  # ref. https://pillow.readthedocs.io/en/latest/installation.html#basic-installation
import os
import time

# directory = r"C:\\Users\\rcxsm\\Downloads\\Sheetmusic\\gefotografeerd\\"
# directory = "C:\Users\rcxsm\Downloads\"

name_of_files = "goede tijden slechte tijden"

extensie = "jpg"
number_of_files = 1
make_files = True
# mode = "list_of_files"
# mode ="easysheetmusic" # https://easysheetmusic.altervista.org/
mode="directory"
def main():
    
    if mode == "list_of_files":

        #         #   r"C:\Users\rcxsm\Downloads\Sheetmusic\gefotografeerd\IMG_4242.JPG"]
        files = [
            r"C:\Users\rcxsm\Downloads\Sheetmusic\gefotografeerd\12102010497.jpg",
            r"C:\Users\rcxsm\Downloads\Sheetmusic\gefotografeerd\12102010498.jpg",
        ]
    elif mode =="directory":
        dir_name = r"C:\Users\rcxsm\Downloads\Sheetmusic\personal fakebook"
        os.chdir(dir_name)  # change directory from working dir to dir with files
        files = []
        for file in os.listdir(dir_name):  # loop through items in dir
            print (file)
            files.append(file)
        name_of_files = "personal_fakebook"


    elif mode == "easysheetmusic":
        
        files = []
        for n in range(number_of_files):
            files.append(r"C:\Users\rcxsm\Downloads" + "\\"+ name_of_files + "-0" + str(n + 1) + "." + extensie)
    else:
        print("Error in Mode {mode}")
    print(files)

 
    #images = [Image.open(f) for f in files]

    pdf_path = r"C:\\Users\\rcxsm\\Downloads\\" + name_of_files + ".pdf"

    Image.open(files[0]).save(
        pdf_path, "PDF", resolution=100.0, save_all=True, 
        append_images=(Image.open(f) for f in files[1:])) 

    
    print(f"{pdf_path} saved")
    time.sleep(1)
    delete=False
    if delete:
        try:
            for f in files:
                os.remove(directory + f)
                print(f"{directory+f} deleted")
        except:
            print("Can't delete file")


if __name__ == "__main__":
    main()
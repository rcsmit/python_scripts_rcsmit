import cv2
import math
from PIL import Image, ExifTags
import os
import re

def correct_image_rotation(image):
    """Many modern cameras and smartphones store orientation information in the image file 
    as EXIF metadata rather than physically rotating the image. When viewing these images in 
    some applications (e.g., image viewers or some PDF readers), they may appear correctly 
    rotated because these applications honor the EXIF orientation metadata. 
    However, PIL.Image.open() doesn't always apply this by default, 
    so we need to manually correct it.

    https://chatgpt.com/c/6706ff08-4a8c-8004-9d62-c1f28cdd7de1
    
    Args:
        image (_type_): _description_

    Returns:
        _type_: _description_
    """    
    try:
        for orientation in ExifTags.TAGS.keys():
            if ExifTags.TAGS[orientation] == 'Orientation':
                break
        exif = image._getexif()
        
        if exif is not None:
            orientation = exif.get(orientation)

            if orientation == 3:
                image = image.rotate(180, expand=True)
            elif orientation == 6:
                image = image.rotate(270, expand=True)
            elif orientation == 8:
                image = image.rotate(90, expand=True) #counter clockwise I think
    except (AttributeError, KeyError, IndexError):
        # If there's no EXIF data or no orientation tag, we skip the rotation.
        pass

    return image
 
def crop_images(dir_name):
    """
    Crop images in the specified directory and save the cropped images.

    Args:
        dir_name (str): The directory containing the images to be cropped.
    """
    for uploaded_image in os.listdir(dir_name): 
        uploaded_image = os.path.join(dir_name, uploaded_image) 
        image = Image.open(uploaded_image)
        
        image = correct_image_rotation(image)
        filename =uploaded_image[:-4]
        # https://gist.github.com/alexlib/ef7df7bfdb3dba1698f4
        imgwidth, imgheight = image.size
        print(('Image size is: %d x %d ' % (imgwidth, imgheight)))
        height = imgheight # np.int(imgheight/2)
        width = int(imgwidth*0.4)
        new_img = Image.new('RGB', (width, height), 255)    
        # Define the cropping box
        left = int(imgwidth * 0.4)
        top = 0
        right = int(imgwidth * 0.8)
        bottom = imgheight
        
        # Crop the image
        cropped_image = image.crop((left, top, right, bottom))
        
                
        new_img.paste(cropped_image)
        filename_tosave = f"{filename}-cropped.jpg"
        print (filename_tosave)
        new_img.save(filename_tosave)

def extractImages(videoFile,imagesFolder):
    """
    Extract frames from a video file and save them as images in the specified folder.

    Args:
        videoFile (str): The path to the video file.
        imagesFolder (str): The folder to save the extracted images.
    """  
    cap = cv2.VideoCapture(videoFile)
    frameRate = cap.get(5) #frame rate
    while(cap.isOpened()):
        frameId = cap.get(1) #current frame number
        ret, frame = cap.read()
        if (ret != True):
            break
        if (frameId % math.floor(frameRate) == 0):
            #filename = imagesFolder + "/image_" +  str(int(frameId)) + ".jpg"
            filename = imagesFolder + "/image_" + f"{int(frameId):06d}" + ".jpg"
   
            cv2.imwrite(filename, frame)
            print (filename)
    cap.release()
    print ("Done!")

def create_image_grid(dir_name, columns, output_filename):
    """
    Create a grid of images from a directory.

    Args:
        dir_name (str): The directory containing the images.
        columns (int): The number of columns in the grid.
        output_filename (str): The filename for the output image.
    """
    images = [Image.open(os.path.join(dir_name, img)) for img in sorted(os.listdir(dir_name)) if img.endswith(('png', 'jpg', 'jpeg'))]
    if not images:
        print("No images found in the directory.")
        return

    # Get the size of the first image
    img_width, img_height = images[0].size

    # Calculate the number of rows needed
    rows = math.ceil(len(images) / columns)

    # Create a new blank image with the appropriate size
    total_width = columns * img_width
    total_height = rows * img_height
    grid_image = Image.new('RGB', (total_width, total_height),(255,255,255))

    # Paste images into the grid
    for i, img in enumerate(images):
        row = i // columns
        col = i % columns
        grid_image.paste(img, (col * img_width, row * img_height))

    # Save the grid image
    grid_image.save(output_filename)
    print(f"Grid image saved as {output_filename}")


def create_multiple_image_grids(dir_name, columns, rows, output_filename_prefix):
    """
    Create multiple grids of images from a directory, each with a specified number of rows.

    Args:
        dir_name (str): The directory containing the images.
        columns (int): The number of columns in each grid.
        rows (int): The number of rows in each grid.
        output_filename_prefix (str): The prefix for the output grid image filenames.
    """
    try:
        images = [Image.open(os.path.join(dir_name, img)) for img in sorted(os.listdir(dir_name)) if img.endswith(('png', 'jpg', 'jpeg'))]
    except Exception as e:
        print(f"Error loading images: {e}")
        return
    
    if not images:
        print("No images found in the directory.")
        return

    # Get the size of the first image
    img_width, img_height = images[0].size

    # Calculate the number of images per grid
    images_per_grid = columns * rows

    # Create grids
    for grid_index in range(0, len(images), images_per_grid):
        grid_images = images[grid_index:grid_index + images_per_grid]

        # Calculate the size of the grid
        total_width = columns * img_width
        total_height = rows * img_height
        grid_image = Image.new('RGB', (total_width, total_height), (255, 255, 255))

        # Paste images into the grid
        for i, img in enumerate(grid_images):
            row = i // columns
            col = i % columns
            grid_image.paste(img, (col * img_width, row * img_height))

        # Save the grid image
        output_filename = f"{dir_name}/{output_filename_prefix}_{grid_index // images_per_grid + 1}.jpg"
        grid_image.save(output_filename)
        print(f"Grid image saved as {output_filename}")

def combine_grids_to_pdf(dir_name, output_pdf_filename, grid_prefix):
    """
    Combine all grid images into a single PDF.

    Args:
        dir_name (str): The directory containing the grid images.
        output_pdf_filename (str): The filename for the output PDF.
        grid_prefix (str): The prefix of the grid image filenames to include in the PDF.
    """
    # Find all grid images with the specified prefix
    grid_images = [
        os.path.join(dir_name, img)
        for img in sorted(os.listdir(dir_name))
        if img.startswith(grid_prefix) and img.endswith(('jpg', 'jpeg', 'png'))
    ]

    if not grid_images:
        print("No grid images found to combine into a PDF.")
        return

    # Open the images and save them as a PDF
    try:
        image_list = [Image.open(img).convert("RGB") for img in grid_images]
        image_list[0].save(output_pdf_filename, save_all=True, append_images=image_list[1:])
        print(f"PDF saved as {output_pdf_filename}")
    except Exception as e:
        print(f"Error saving PDF: {e}")
    
def rename_files_with_4digit_numbers(dir_name):
    """
    Rename files in the directory to have 4-digit numbers in their filenames.

    Args:
        dir_name (str): The directory containing the images.
    """
    for filename in os.listdir(dir_name):
        match = re.search(r'(\d+)', filename)
        if match:
            number = int(match.group(1))
            new_filename = re.sub(r'\d+', f'{number:04d}', filename)
            os.rename(os.path.join(dir_name, filename), os.path.join(dir_name, new_filename))
            print(f'Renamed: {filename} to {new_filename}')

def add_prefix(dir_name, prefix):
    """
    Rename files in the directory to have 4-digit numbers in their filenames.

    Args:
        dir_name (str): The directory containing the images.
    """
    for filename in os.listdir(dir_name):
        os.rename(os.path.join(dir_name, filename), os.path.join(dir_name, f"{prefix}_{filename}"))
                                                                 
        print(f'Renamed: {filename} to {prefix}_{filename}')

def main():
    videoFile = r"C:\Users\rcxsm\Downloads\received_655525212783735.mp4"
    videoFile = r"C:\Users\rcxsm\Music\MET PYTHON GEDOWNLOAD\Training VDO Driving Licences in Thailand.mp4"
    imagesFolder = r"C:\Users\rcxsm\Documents\python_scripts\output\dlt"
    if 1==2:    
        # FIRST WE EXTRACT THE IMAGES
        extractImages(videoFile,imagesFolder)

        # THEN WE CROP THE IMAGES
        # crop_images(imagesFolder)

        # THEN WE RENAME THE FILES TO HAVE 4-DIGIT NUMBERS SO THE SORTING IS RIGHT
        rename_files_with_4digit_numbers(imagesFolder)
        
        # TAKE OUT THE IMAGES WE DONT WANT IN TE GRID (manually)


    # THEN WE CREATE A GRID IMAGE
    
    # create_image_grid(imagesFolder, 3, imagesFolder+'\\output_grid.jpg')
    create_multiple_image_grids(imagesFolder, 4,12, "_output_grid")
   
    # Combine grids into a single PDF
    combine_grids_to_pdf(imagesFolder, r"C:\Users\rcxsm\Documents\python_scripts\output\dlt\combined_grids.pdf", "_output_grid")

    # add prefix to all files in the directory
    #add_prefix(r"C:\Users\rcxsm\Documents\python_scripts\output\dlt\q2", "q2_")

if __name__ == "__main__":  
    main()
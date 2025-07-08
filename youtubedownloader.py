# pylint: disable=line-too-long
# -*- coding: utf-8 -*-
"""
Created on Fri Nov 29 16:46:42 2019

@author: rcxsm

"""
import os

import os.path
import re
import shutil
from random import randint
import requests
from keys import *


from datetime import datetime

import time
import sys
import subprocess
import requests
# from pytube import YouTube
# import pytube

# import pytube.request
from pytube import Playlist
import pytubefix as pytube
from pytubefix import YouTube

# from pytube.cli import on_progress

# from time import sleep

from moviepy.video.io.ffmpeg_tools import ffmpeg_extract_subclip
import win32clipboard  # part of pywin32


def convert_single_file_to_mp3(mp4, delete_original):
    """convert a mp4 to mp3

    Args:
        mp4 (str): url / file
        delete_original (boolean): Delete Orignal?
    """

    if right(mp4, 7) == "mp4.mp4":
        mp3 = left(mp4, (len(mp4) - 7)) + ".mp3"
    else:
        mp3 = left(mp4, (len(mp4) - 4)) + ".mp3"

    # Converting - Not needed anymore since MP3's are downloaded directly
    print(f"Converting... {mp4}")
    subprocess.call(
        [
            "C:\\Users\\rcxsm\\Music\\MET PYTHON GEDOWNLOAD\\ffmpeg.exe",
            "-i",
            mp4,
            mp3,
        ],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    if delete_original:
        os.remove(mp4)


def cleanup(test_string):
    """Avoid forbidden characters in file names

    Args:
        test_string (string): the string to test

    Returns:
        result_string (string) : string without the bad characters
    """
    bad_chars = [
        ":",
        ";",
        ",",
        "/",
        ":",
        "!",
        "?",
        "|",
        '",' "'",
        "*",
        "(",
        ")",
        "[",
        "]",
        "„",
        ".",
        '"',
    ]
    result_string = "".join(i for i in test_string if not i in bad_chars)
    # result_string = result_string.replace(" ", "_")
    return result_string


def left(s, amount):
    """_summary_

    Args:
        s (_type_): _description_
        amount (_type_): _description_

    Returns:
        _type_: _description_
    """
    return s[:amount]


def right(s, amount):
    """_summary_

    Args:
        s (_type_): _description_
        amount (_type_): _description_

    Returns:
        _type_: _description_
    """
    return s[-amount:]


def mid(s, offset, amount):
    """_summary_

    Args:
        s (_type_): _description_
        offset (_type_): _description_
        amount (_type_): _description_

    Returns:
        _type_: _description_
    """
    return s[offset - 1 : offset + amount - 1]


def import_facebook_video():
    """_summary_"""
    url = "Fb_Video_URl"

    request = requests.get(url)
    video_url = re.findall(f"{'hd_src'}:\"(.+?)\"", request.text)[0]
    filename = datetime.now().strftime(r"%d%b%Y%H%M%S" + ".mp4")

    print("<===Downloading video===>")
    request = requests.get(video_url)

    with open(filename, "wb") as f:
        f.write(request.content)


def countdown(t):
    """Creating a countdown timer to show the wait time

        https://www.geeksforgeeks.org/how-to-create-a-countdown-timer-using-python/
    Args:
        t (integer): Wait time in seconds
    """
    while t:
        mins, secs = divmod(t, 60)
        timer = "{:02d}:{:02d}".format(mins, secs)
        print(f"Waiting : {timer}", end="\r")
        time.sleep(1)
        t -= 1


def crop_file(inputfile, outputfile, start, duration):
    """[summary]

    Args:
        input (string): input filename
        output (string): output filename
        from (int): start point (in seconds)
        duration (int): length in seconds
    """

    # ffmpeg -ss 30 -t 70 -i inputfile.mp3 -acodec copy outputfile.mp3
    print(f"cropping... {inputfile}")

    subprocess.call(
        [
            "C:\\Users\\rcxsm\\Music\\MET PYTHON GEDOWNLOAD\\ffmpeg.exe",
            "-ss",
            str(start),
            "-t",
            str(duration),
            "-i",
            inputfile,
            "-acodec",
            "copy",
            outputfile,
        ],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )

    print(f"Saved as... {outputfile}")


def crop_file_video(inputfile, start_time, end_time):
    """_summary_

    Args:
        inputfile (_type_): _description_
        start_time (_type_): _description_
        end_time (_type_): _description_

    Returns:
        _type_: _description_
    """
    outputfile = "cropped_" + inputfile
    ffmpeg_extract_subclip(inputfile, start_time, end_time, targetname=outputfile)
    os.remove(inputfile)
    return outputfile


def download_file(durl, path_to_save, what, start_time, end_time, convert):
    """Download a file"""

    def on_progress(stream, chunk, bytes_remaining):
        """Callback function"""
        total_size = stream.filesize
        bytes_downloaded = total_size - bytes_remaining
        # pct_completed = bytes_downloaded / total_size * 100
        display_progress_bar(bytes_downloaded, total_size)

    def display_progress_bar(
        bytes_received: int, filesize: int, ch: str = "█", scale: float = 0.55
    ) -> None:
        """Display a simple, pretty progress bar.

        Example:
        ~~~~~~~~
        PSY - GANGNAM STYLE(강남스타일) MV.mp4
        ↳ |███████████████████████████████████████| 100.0%

        :param int bytes_received:
            The delta between the total file size (bytes) and bytes already
            written to disk.
        :param int filesize:
            File size of the media stream in bytes.
        :param str ch:
            Character to use for presenting progress segment.
        :param float scale:
            Scale multiplier to reduce progress bar size.

        """
        columns = shutil.get_terminal_size().columns
        max_width = int(columns * scale)

        filled = int(round(max_width * bytes_received / float(filesize)))
        remaining = max_width - filled
        progress_bar = ch * filled + "." * remaining
        percent = round(100.0 * bytes_received / float(filesize), 1)
        text = f" ↳ |{progress_bar}| {percent}%  ({round(bytes_received/1048576,1)}/{round(filesize/1048576,1)} MB)\r"
        sys.stdout.write(text)
        sys.stdout.flush()
    if durl is not None:
        s1 = int(time.time())
        # Title and Time
        # try:
        print((YouTube(durl)).title)
        title = cleanup(((YouTube(durl)).title))
        # title = "Christina Perri - A Thousand Years captured in The Live Room.mp4"
        # except:
        #    print ("Not a valid video URL and/or no video found")
        #    sys.exit()

        pytube.request.default_range_size = int(1048576 / 1)  # 9437184
        _filename = title
        mp4 = f"{_filename}.mp4"
        mp3 = f"{_filename}.mp3"

        if os.path.isfile(mp4) or os.path.isfile(mp3):
            print(f"File [{mp4}] exist already. I stop")
            return

        print(f"Downloading.... {_filename}")

        if what == "audio":
            # YouTube(durl).streams.first().download(filename=mp4)       # for music
            YouTube(durl, on_progress_callback=on_progress).streams.get_by_itag(
                140
            ).download(filename=mp4)
            # filesize = YouTube(durl).streams.get_by_itag(140).filesize
            # print (f"Filesize = {round(filesize/1048576,2)} MB)")
            print(" ")
            if start_time is None:
                new_filename = (
                    left(mp4, (len(mp4) - 4)) + ".mp4"
                )  # for some reason files are saved as namemp4.mp4
            else:
                new_filename = crop_file_video(mp4, start_time, end_time)
        
            if convert:
                convert_single_file_to_mp3(new_filename, True)

        elif what == "video":
            YouTube(durl, on_progress_callback=on_progress).streams.get_by_itag(
                18
            ).download(
                filename=mp4
            )  # for video 360p
            # filesize = YouTube(durl).streams.get_by_itag(18).filesize
            # print (f"Filesize = {round(filesize/1048576,2)} MB)")
            if start_time is None:
                new_filename = (
                    left(mp4, (len(mp4) - 4)) + ".mp4"
                )  # for some reason files are saved as namemp4.mp4
            else:
                new_filename = crop_file_video(mp4, start_time, end_time)

        s2 = int(time.time())
        s2x = s2 - s1
        print(" ")  # to compensate the  sys.stdout.flush()

        print(f"Downloading  took {str(s2x)} seconds ....)")
    else:
        print ("Nothing downloaded")


def download_playlist(url, path_to_save, what, ask, wait, start):
    """Downlaods the sound of the videos in a playlist

    Args:
        url (_type_): _description_
        path_to_save (_type_): _description_
        what (_type_): _description_
        ask (_type_): _description_
        wait (_type_): _description_
        start (_type_): start time in seconds
    """
    try:
        playlist = Playlist(url)
    except:
        print("Not a valid list URL and/or no list/videos found")
        sys.exit()
    print (playlist)
    what = "audio" # "video"
    start_time, end_time =   None, None 
    path_to_save = r"C:\\Users\\rcxsm\\Music\\MET PYTHON GEDOWNLOAD\\"
    convert, ask, wait =True, False, False  # ask if you want to download each file  # wait a random number of seconds in between the downloads
    get_clipboard, get_url_list = False, True

    for durl in playlist:
        download_file(durl, path_to_save, what, start_time, end_time, convert)
    if 1==2:
        # DEOSNT WORK ANYMORE

        # this fixes the empty playlist.videos list
        playlist._video_regex = re.compile(r"\"url\":\"(/watch\?v=[\w-]*)")
        stop = 9990
        # test purposes

        for n, video in enumerate(playlist.videos):
            
            if n >= start and n < stop:
                #try:
                if 1==1: 
                    mp4 = cleanup(video.title) + ".mp4"
                    if ask:
                        dl_yes = input(
                            f"Download {n+1}/{len(playlist.video_urls)} - {video.title} ? (y/n/q) "
                        )
                    else:
                        dl_yes = "y"

                    if dl_yes == "y" or dl_yes == "Y":
                        print(
                            f"Downloading {n+1}/{len(playlist.video_urls)} - {video.title}"
                        )

                        if what == "audio":
                            # video.streams.first().download(filename=mp4)       # for music
                            video.streams.get_by_itag(140).download(filename=mp4)
                            new_filename = path_to_save + left(mp4, (len(mp4) - 4)) + ".mp4"
                            convert_single_file_to_mp3(new_filename, True)

                        elif what == "video":
                            video.streams.get_by_itag(18).download(
                                filename=mp4
                            )  # for video 360p

                        if wait:
                            wait_time = randint(10, 30)
                            countdown(wait_time)

                    elif dl_yes == "q" or dl_yes == "Q":
                        sys.exit()
                # except SystemExit:
                #     print()
                #     print("Thank you for using this script.")
                #     sys.exit()
                # except Exception as e:
                #     print(
                #         f"ERROR Downloading or finding the name of  {n+1}/{len(playlist.video_urls)}\n{e}                     "
                #     )
                #     # some videos give 403 error
                #     # too lazy to implement this (yet)
                #     # https://github.com/pytube/pytube/issues/399

        convert_all_files_in_directory_to_mp3(path_to_save)


def convert_all_files_in_directory_to_mp3(path):
    """Convert all files in directory to MP3

    Args:
        path ([type]): [description]
    """
    s1 = int(time.time())
    number_of_files = 0
    with os.scandir(path) as it:
        for entry in it:
            if entry.name.endswith(".mp4") and entry.is_file():

                mp4 = str(entry.path)

                convert_single_file_to_mp3(mp4, True)
                number_of_files += 1

    print(
        f"COMPLETE - Totaal  {int(time.time() -s1)} sec. | {number_of_files} files => {round((time.time() -s1) / number_of_files)} sec. per file"
    )


def main_download(
    path_to_save,
    what: str,
    start_time: int,
    end_time: int,
    convert: bool,
    get_clipboard: bool,
    get_url_list: bool,
    url_list: list[str],
    ask: bool,
    wait: bool,
) -> None:

    """_summary_"""
    current_path = os.getcwd()

    # os.chdir("C:\\Users\\rcxsm\\Music\\MET PYTHON GEDOWNLOAD\\")
    os.chdir(path_to_save)

    if get_url_list:
        for i,u in enumerate(url_list):
            print (f"=== {i+1} / {len(url_list)} ===")
            download_file(u, path_to_save, what, start_time, end_time, convert)

    else:
        if get_clipboard:
            win32clipboard.OpenClipboard()
            url = win32clipboard.GetClipboardData()
            win32clipboard.CloseClipboard()
            if "youtube.com" in url:
                print(f"Retrieving {url}")
            else:
                url = input("URL to download (q = quit): ")

        else:
            url = input("URL to download (q = quit): ")
        if url == "q":
            print("OK. Doei")
            quit()
        if "list" in url:

            to_start_ = 0 # input("Where to start ? ")
            if to_start_ is None or to_start_ == "":
                start = 0
            else:
                start = int(to_start_) - 1
            download_playlist(url, path_to_save, what, ask, wait, start)
        else:
            download_file(url, path_to_save, what, start_time, end_time, convert)
    os.chdir(current_path)


def add_pretext(directory):
    """Add a string in front of the current filename in a current directory

    Args:
        directory (_type_): _description_
    """    
    import os

    # Iterate through each file in the directory
    for filename in os.listdir(directory):
        # Check if the file is a regular file (not a directory)
        if os.path.isfile(os.path.join(directory, filename)):
            # Construct the new filename with "Taylor Swift - TTPD - " prefix
            new_filename = f"Taylor Swift - TTPD - {filename}"
            # Rename the file
            os.rename(os.path.join(directory, filename), os.path.join(directory, new_filename))



def find_first_youtube_video(search ):
    """
    Finds the first YouTube video for a given search query.

    This function uses the YouTube Data API to search for videos based on the provided 
    search query. It retrieves the first video result and returns its YouTube URL.


    To set up the YouTube API, follow these steps:

    1. **Go to the Google Cloud Console**:
    - Visit: [Google Cloud Console](https://console.cloud.google.com/)

    2. **Create a Project**:
    - In the Google Cloud Console, click on the project dropdown and select **New Project**. Provide a name for your project and click **Create**.

    3. **Enable the YouTube Data API**:
    - Navigate to the YouTube API page: [YouTube API](https://console.cloud.google.com/apis/api/youtube.googleapis.com/)
    - Click **Enable** to enable the API for your project.

    4. **Create Credentials**:
    - Go to the **Credentials** page: [Credentials](https://console.cloud.google.com/auth/clients)
    - Click **Create Credentials** and select **API Key** or **OAuth 2.0 Client ID** (depending on your needs). If you're using OAuth, follow the steps to set up consent screens and redirect URIs.

    5. **Obtain API Key/Client ID**:
    - After creating your credentials, you'll be able to download or copy your **API Key** or **Client ID**, which you'll use to authenticate API requests.
    - the key is in keys.py as api_key_youtube. Don't forget to add it to the .gitignore file if you are using git. 

    6. **API Metrics**:
    - To view API usage metrics, visit: [API Metrics](https://console.cloud.google.com/apis/api/youtube.googleapis.com/metrics?project=project_name)

    7. ** Usage**:
    https://developers.google.com/youtube/v3/determine_quota_cost
    A search costs 100 credits. The quota is normally 10_000 credits per day. (so 100 searches)
    
    - Make sure to read the API documentation to understand how to use the API effectively and what quota limits apply to your project.
    - You can find the API documentation here: [YouTube Data API v3](https://developers.google.com/youtube/v3/docs) 

    Once you have completed these steps, you can start making requests to the YouTube Data API using the provided credentials.
    Setup API:
    https://console.cloud.google.com/
    https://console.cloud.google.com/auth/clients
    https://console.cloud.google.com/apis/api/youtube.googleapis.com/ - ["Credentials"]

    Metrics: [Click the tab "quota & system limits"]
    https://console.cloud.google.com/apis/api/youtube.googleapis.com/metrics?project=gpxanalyzer-454406
    
    Args:
        search (str): The search query string to look for on YouTube.

    Returns:
        str: The URL of the first YouTube video matching the search query.

    Raises:
        Exception: If the API request fails (e.g., invalid API key, network issues).
        KeyError: If no video is found for the given search query.

    Notes:
        - The function requires a valid YouTube Data API key, which should be stored 
          in the `api_key_youtube` variable.
        - Ensure that the API key has sufficient quota and access to the YouTube Data API.

    Example:
        >>> find_first_youtube_video("Taylor Swift - Love Story")
        'https://www.youtube.com/watch?v=8xg3vE8Ie_E'
    """
    search_url = "https://www.googleapis.com/youtube/v3/search"
    params = {
        "part": "snippet",
        "q": search,
        "type": "video",
        "maxResults": 1,
        "key": api_key_youtube
    }
    response = requests.get(search_url, params=params)
    if response.status_code != 200:
        if response.status_code == 403:
            print("API request failed with status code 403: Forbidden. Check your API key and quota.")
        else:
            print(f"API request failed with status code {response.status_code}")
        return None, None
    else:
        data = response.json()
    
        if "items" not in data or not data["items"]:
            raise KeyError("No video found")
        
        video_id = data["items"][0]["id"]["videoId"]

        video_title = data["items"][0]["snippet"]["title"]
        

        link = f"https://www.youtube.com/watch?v={video_id}"
        return link, video_title


def download_tracklist(trackstring, timestamp_regex, mix_title, mix_url):
    """Downloads a list of tracks from YouTube as audio or video files.

    This function takes a predefined list of track titles, searches for the first 
    YouTube video matching each title using the `find_first_youtube_video` function, 
    and downloads the corresponding audio or video files. The downloaded files are 
    saved to a specified directory.

    Steps:
    1. Searches YouTube for each track in the `tracklist`.
    2. Collects the URLs of the first matching video for each track.
    3. Downloads the audio or video files based on the specified settings.

    Args:
        trackstring : The tracklist as one long string, seperated with \\n
        timestamp_regex : The timestamp regex, eg. r"\\d{2}:\\d{2}" (but one backlash)
        mix_title : The title of the mix
        mix_url : The URL of the mix
    Returns:
        None

    Notes:
        - The `find_first_youtube_video` function is used to fetch the first YouTube 
          video link for each track.
        - The `main_download` function handles the downloading process.
        - The download settings (e.g., audio/video, save path, etc.) are configurable 
          within the function.

    Example:
        To download the predefined tracklist as audio files:
        >>> download_tracklist()

    """   
  
    what = "audio" # "video"
    start_time, end_time =   None, None 
    path_to_save = r"C:\\Users\\rcxsm\\Music\\MET PYTHON GEDOWNLOAD\\"
    convert, ask, wait =True, False, False  # ask if you want to download each file  # wait a random number of seconds in between the downloads
    get_clipboard, get_url_list = False, True
    
    tracklist = trackstring.split("\n")
    
    with open(f"{path_to_save}\\tracklist.txt", "a", encoding="utf-8") as file:
        # Append the details to the file with the current date and time
        # Get the current date and time
        current_datetime = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        file.write(f"\n====================================\n")       
        file.write(f"{current_datetime}\n")
        file.write(f"{mix_title}\n")
        file.write(f"{mix_url}\n")
            
        url_list = []
        for i, track in enumerate(tracklist):
            
            # Remove timestamps using regex
            track = re.sub(timestamp_regex, "", track).strip()
            
            link, video_title = find_first_youtube_video(track)
            
            # Append the details to the file
            file.write(f"{track} | {video_title} | {link}\n")
            
            print (f"--- {i+1}/{len(tracklist)} ---\n{track}\n{video_title}\n{link}\n")
            url_list.append(link)
    print (url_list)   
    
    
    if 1==1:
        main_download(
            path_to_save,
            what,
            start_time,
            end_time,
            convert,
            get_clipboard,
            get_url_list,
            url_list,
            ask,
            wait,
        )

def main_download_tracklist():
    """--- Downloads a list of tracks from YouTube as audio or video files. ---"""
    trackstring  ="""1. Underworld - Born Slippy
2. Floorplan - Never Grow Old
3. Hardfloor - Acperience 1
4. Josh Wink - Higher State of Consciousness (Tweekin Acid Funk)
5. Rolando - Knight of the Jaguar
6. Donna Summer - I Feel Love
7. Oxia - Domino
8. Octave One - Black Water
9. Green Velvet - Flash
10. Fischerspooner - Emerge
Jaydee - Plastic Dreams 
Destination - Definition of Love (G-Flame and Mr G remix)
Smith and Selway - Move
Agoria - La onzieme marche (Phil Kieran mix)
Renato Cohen - Pontape
Nathan Fake - The sky was pink (James Holden mix)
Sabres of Paradise - Smokebelch (David Holmes remix)
Plastikman - Spastik
Matador - Kingswing
Bryan Zentz - D clash
Josh Wink - Don't laugh
Joey beltram energy flash
Hardfloor acaperiance
Laurent garnier crispy bacon
Paragon 1 the deliverer
The sabres of paradise
Robert armani circus bells
Jeff Mills- Step to enchantment
Laurent Garnier - Crispy bacon
Dense n Pika- Louder than a bomb
Joey Beltram- Energy flash
Joey Beltram - the Fuzz
Hardfloor- Acperience
Octave one - the 3rd degree
Commander Tom - R am eye
Funk d void. - Bad coffee
Slam - Positive education"""

    mix_title ="Acroyoga"
    mix_url = "https://www.xxxx.com"
    #timestamp_regex = r"\d{2}:\d{2}
    timestamp_regex = r"\d{1,2}. " # 1 or 2 digits, followed by a dot and a space  

    download_tracklist(trackstring, timestamp_regex, mix_title, mix_url )


def main():
    """_summary_
    """

    #what = "video"
    
    what = "audio"
    start_time =   None # 9 # None # 12 # None# 45  # (1*60)+54 #None # 1.1 # None # 0 # None #144 #198 # None# 5 # None #(0*60)+28 # None #131 # None # 83 #none
    end_time = None # (4 * 60) + 15  # None  #    #311
    path_to_save = r"C:\\Users\\rcxsm\\Music\\MET PYTHON GEDOWNLOAD\\"
    convert = True
    ask = False  # ask if you want to download each file
    wait = True  # wait a random number of seconds in between the downloads
    get_clipboard = True
    get_url_list = False

    # get_clipboard = False
    #
    # get_url_list = True
    

    # DOWNLOAD AUDIO OR VIDEO FROM A URL OR LIST
    #url_list =['https://www.youtube.com/watch?v=6TYsOMYaz6E', 'https://www.youtube.com/watch?v=605bwlAz_iQ', 'https://www.youtube.com/watch?v=SnnwwWY4uMU', 'https://www.youtube.com/watch?v=5IrHzrg4qdQ', 'https://www.youtube.com/watch?v=aU6z-pPEmY0', 'https://www.youtube.com/watch?v=DwpedKWwS3w', 'https://www.youtube.com/watch?v=uu9u_gesIfo', 'https://www.youtube.com/watch?v=jgVrX1u9afY', 'https://www.youtube.com/watch?v=l-vSl7BuxGs', 'https://www.youtube.com/watch?v=XwX9w00dZcY', 'https://www.youtube.com/watch?v=NiBQ-WLL84E', 'https://www.youtube.com/watch?v=JZfJTSlhOXM']
    
    url_list = ['https://www.youtube.com/watch?v=vl9p7Sd_ZaE', 'https://www.youtube.com/watch?v=RRQyyKaTFNA', 'https://www.youtube.com/watch?v=WZS6hpgkxOU', 'https://www.youtube.com/watch?v=U4ByNuRtTFI', 'https://www.youtube.com/watch?v=fJkAHiiIY6M', 'https://www.youtube.com/watch?v=6K-ifQV1gjU', 'https://www.youtube.com/watch?v=aSwQL1o4u5Q', 'https://www.youtube.com/watch?v=B_UBYDdO3lk', 'https://www.youtube.com/watch?v=kObuc3KyTaE', 'https://www.youtube.com/watch?v=4n_fKoXmjCs', 'https://www.youtube.com/watch?v=Zce5WnphEkg', 'https://www.youtube.com/watch?v=_Y0seJSuRak', 'https://www.youtube.com/watch?v=rMJpDYzazfI', 'https://www.youtube.com/watch?v=ibof3M0pZZ0', 'https://www.youtube.com/watch?v=KYdMHXfgdjk', 'https://www.youtube.com/watch?v=z3hef-Y16g0', 'https://www.youtube.com/watch?v=Eg5qYmTRpes', 'https://www.youtube.com/watch?v=-m0vC9BlQ3I', 'https://www.youtube.com/watch?v=lTdzWjzbsN8', 'https://www.youtube.com/watch?v=TStYHJuC8To', 'https://www.youtube.com/watch?v=bObN_VOXRPs', 'https://www.youtube.com/watch?v=NSDBqfNHOK8', 'https://www.youtube.com/watch?v=lZ4-fLdTLss', 'https://www.youtube.com/watch?v=oaVA1fnzczI', 'https://www.youtube.com/watch?v=4bIe8M8qXJ8']
    main_download(
        path_to_save,
        what,
        start_time,
        end_time,
        convert,
        get_clipboard,
        get_url_list,
        url_list,
        ask,
        wait,
    )
    # BATCH CONVERT FILES IN A DIRECTORY FROM MP4 to MP3
    # convert_all_files_in_directory_to_mp3("C:\\Users\\rcxsm\\Music\\MET PYTHON GEDOWNLOAD\\toconvert\\")

    # CONVERT A SINGLE FILE
    # convert_single_file_to_mp3("C:\\Users\\rcxsm\\Music\\MET PYTHON GEDOWNLOAD\\nieuw\\Taylor Swift - Everything Has Changed ft Ed Sheeranmp4.mp4")

if __name__ == "__main__":
    
    # ----convert a mp4 to mp3 -----
    # mp4=r"C:\Users\rcxsm\Music\MET PYTHON GEDOWNLOAD\TAYLOR SWIFT ERAS TOUR Full Show Front Row Live in Edinburgh & Liverpool 7 & 14 June 2024.mp4"
    # convert_single_file_to_mp3(mp4, False)
    
        
    # --- Add a string in front of the current filename in a current directory ---
    # directory = "C:\\Users\\rcxsm\\Music\\MET PYTHON GEDOWNLOAD\\ttpd\\" 
    # add_pretext(directory)

    main()
    #main_download_tracklist()
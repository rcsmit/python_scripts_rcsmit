import re
from pytube import Playlist

# https://stackoverflow.com/questions/54710982/using-pytube-to-download-playlist-from-youtube

#url = input("URL: ")
url = "https://www.youtube.com/watch?list=PLTo6svdhIL1cxS4ffGueFpVCF756ip-ab"
YOUTUBE_STREAM_AUDIO = '140' # modify the value to download a different stream
DOWNLOAD_DIR = '"C:\\Users\\rcxsm\\Documents\\pyhton_scripts\\output'

playlist = Playlist(url)

# this fixes the empty playlist.videos list
playlist._video_regex = re.compile(r"\"url\":\"(/watch\?v=[\w-]*)")

print(len(playlist.video_urls))

for url in playlist.video_urls:
    print(url)

# physically downloading the audio track
for n,video in enumerate(playlist.videos):
    print (f"Downloading {n}/{len(playlist.video_urls)}")
    audioStream = video.streams.get_by_itag(YOUTUBE_STREAM_AUDIO)
    audioStream.download()
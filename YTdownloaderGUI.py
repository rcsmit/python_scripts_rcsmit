# -*- coding: utf-8 -*-
"""
Created on Sun Dec 15 09:51:16 2019

@author: rcxsm
"""


import PySimpleGUI as sg

from pytube import YouTube
import os
import subprocess
import time

def cleanup(test_string):   
    bad_chars = [';', ',', '/', ':', '!', "'","*"] 
    result_string = ''.join(i for i in test_string if not i in bad_chars) 
    result_string = result_string.replace(" ", "_")  
    return result_string
  

def download(durl):
    s1 = (int(time.time()))
     # Title and Time
    print("...")
    print(((YouTube(durl)).title))
    print (durl)
    print("...")
    title=cleanup(((YouTube(durl)).title))
    
    # Filename specification
    _filename = (title)
     
    # Downloading
    print("Downloading....")
    YouTube(durl).streams.first().download(filename=_filename)
    
    s2 = (int(time.time()))
    s2x = s2-s1
    print("Downloading took " + str(s2x) + " seconds ....")
    # Converting
    print("Converting....")
    
    mp4 = "%s.mp4" % _filename
    mp3 = "%s.mp3" % _filename
        
    os.chdir('C://Users/rcxsm/Documents/pyhton_scripts/')
    subprocess.call(['ffmpeg', '-i', mp4, mp3])
    
    s3 = (int(time.time()))
    s4 = s3-s1
    print ("\nCOMPLETE - Totaal aantal sec : "+ str(s4))

def downloadplaylist(url):
    pl = Playlist(url)
    n=1
    pl.populate_video_urls()  # fills the pl.video_urls with all links from the playlist
    urls = pl.video_urls
    lengte = (len(pl.video_urls))
    for xurl in urls:
        print ("------------------------------------------")
        print ( str(n) + " out of " + str(lengte))
        print (xurl)
        download (xurl)
        n=n+1
  
def dosomething(url):
    #window.FindElement('output').Update('')
    if "list" in url:
        downloadplaylist(url)
        sg.popup('Completed')

    else:
        download(url)
        #print (url)   
        sg.popup('Completed')
    
def main():
    sg.change_look_and_feel('Material2')	# Add a touch of color
    # All the stuff inside your window.
    layout = [  [sg.Text('YouTube URL')],
                [sg.Text('Paste here'), sg.InputText()],
                [sg.Output(size=(88, 20))],
                [sg.Button('Ok'), sg.Button('Cancel')] ]
                
    
    # Create the Window
    window = sg.Window('YouTube downloader', layout)

     
    
    # Event Loop to process "events" and get the "values" of the inputs
    while True:
        event, values = window.read()
        if event in (None, 'Cancel'):	# if user closes window or clicks cancel
            break
        print('You entered ', values[0])
        dosomething(values[0])
    window.close()

main()


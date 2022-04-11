from pytube import YouTube
YouTube('https://www.youtube.com/watch?v=Ctr0tSg-QzY').streams.first().download()
print ("ok")
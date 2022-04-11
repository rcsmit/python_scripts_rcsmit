import pyttsx3
import time

def countdown(t):
    """ Creating a countdown timer to show the wait time

        https://www.geeksforgeeks.org/how-to-create-a-countdown-timer-using-python/
    Args:
        t (integer): Wait time in seconds
    """
    while t:
        mins, secs = divmod(t, 60)
        timer = '{:02d}:{:02d}'.format(mins, secs)
        print(f"  Waiting : {timer}", end="\r")
        time.sleep(1)
        t -= 1
    print (" ")

# initialise the pyttsx3 engine
engine = pyttsx3.init()
wait_time = 1
# voices = engine.getProperty('voices')

# for voice in voices:

#         print(voice.id)

# convert text to speech
rate = engine.getProperty('rate')   # getting details of current speaking rate
print (rate)                        #printing current voice rate
engine.setProperty('rate', 75)     # setting up new voice rate
for i in range (10,0, -1):
    to_say_in = str(i) + " in"
    to_say_out = str(i) + " out"
    print (to_say_in)
    engine.say(to_say_in)
    engine.runAndWait()
    countdown(wait_time)
    print (to_say_out)
    engine.say(to_say_out)
    engine.runAndWait()
    countdown(wait_time)
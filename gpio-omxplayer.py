import wiringpi
from omxplayer.player import OMXPlayer
from pathlib import Path
import random

# Videos: One non-scary looping idle video and several
# scary ones. Video from atmosfx.com.
idleVideo = Path("PP_Buffer_Wall_Spotlight_H.mp4")
scareVideos = [Path("PP_StartleScare1_Wall_Spotlight_H.mp4"),
               Path("PP_StartleScare2_Wall_Spotlight_H.mp4"),
               Path("PP_StartleScare3_Wall_Spotlight_H.mp4")]


# omxplayer control. One player object at a time, playback starts
# at player construction. We can quit() and start a new video at
# any time.
player = {}
isPlaying = False
def quitPlayer():
    global player
    global isPlaying
    
    try:
        print("quit")
        isPlaying = False
        player.quit()
    except:
        pass

def playFile(path):
    global player
    global isPlaying
    
    quitPlayer()
    
    print("play {0}".format(path))
    isPlaying = True;
    player = OMXPlayer(path, args=["--video_fifo", "10"])
    while not player.is_playing():
        wiringpi.delay(50)

# Monitor GPIO pin for signal from motion detector and interrupt
# the idle video (but don't interrupt the scary video)
PIN_TO_SENSE = 14
idleLoop = True
scareTriggered = False

def gpio_callback_rising():
    print("gpio pin rising")
    global idleLoop
    global scareTriggered
    if not scareTriggered:
        print("SCARE")
        idleLoop = False
        scareTriggered = True
        quitPlayer()

wiringpi.wiringPiSetupGpio()
wiringpi.pinMode(PIN_TO_SENSE, wiringpi.GPIO.INPUT)
wiringpi.pullUpDnControl(PIN_TO_SENSE, wiringpi.GPIO.PUD_DOWN)
wiringpi.wiringPiISR(PIN_TO_SENSE, wiringpi.GPIO.INT_EDGE_RISING, gpio_callback_rising)

# Main playback loop. Play the idle video back-to-back, unless
# it's scare time, in which case play one of the scary videos.
while True:
    try:
        print("loop")
        if idleLoop:
            playFile(idleVideo)
        else:
            video = random.randint(0,len(scareVideos))
            playFile(scareVideos[video])
        
        if idleLoop:
            scareTriggered = False        
        idleLoop = True;
        try:
            while isPlaying and player.is_playing():
                wiringpi.delay(50)
        except:
            pass
    
    except Exception as e:
        print(e)
        pass
    

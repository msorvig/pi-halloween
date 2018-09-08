import wiringpi
from omxplayer.player import OMXPlayer
from pathlib import Path
import random
import mode2ir
import threading

# Videos: One non-scary looping idle video and several
# scary ones. Video from atmosfx.com.

videoSeries = [
    { "idleVideo"   : Path("BOO_Buffer_Holl_H.mp4"),
      "scareVideos" : [ Path("BOO_BooTime_Holl_H.mp4") ]
    },
    { "idleVideo"   : Path("PP_Buffer_Wall_Spotlight_H.mp4"),
      "scareVideos" : [ Path("PP_StartleScare1_Wall_Spotlight_H.mp4"),
                        Path("PP_StartleScare2_Wall_Spotlight_H.mp4"),
                        Path("PP_StartleScare3_Wall_Spotlight_H.mp4") ]
    }
]

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

series = 0
idleLoop = True
scareEnabled = True
scareTriggered = False

# trigger a random scare video, but only if enabled and
# we are not already playing a scary video.
def triggerScaryVideo():
    global idleLoop
    global scareTriggered
    if not scareTriggered and scareEnabled:
        print("SCARE (triggerScaryVideo)")
        idleLoop = False
        scareTriggered = True
        quitPlayer()
    
# unconditionally play a scary video
def playScaryVideo():
    global idleLoop
    global scareTriggered
    print("SCARE (playScaryVideo)")
    idleLoop = False
    scareTriggered = True
    quitPlayer()
    
# unconditionally play the idle video
def playIdleVideo():
    global idleLoop
    global scareTriggered
    print("playIdleVideo")
    idleLoop = True
    scareTriggered = False
    quitPlayer()

# Monitor GPIO pin for signal from motion detector and interrupt
# the idle video.
PIN_TO_SENSE = 14
def gpio_callback_rising():
    print("gpio pin rising")
    triggerScaryVideo()

wiringpi.wiringPiSetupGpio()
wiringpi.pinMode(PIN_TO_SENSE, wiringpi.GPIO.INPUT)
wiringpi.pullUpDnControl(PIN_TO_SENSE, wiringpi.GPIO.PUD_DOWN)
wiringpi.wiringPiISR(PIN_TO_SENSE, wiringpi.GPIO.INT_EDGE_RISING, gpio_callback_rising)

# IR Remote decode loop for the "Syvio" remote control
def handleKey(key):
    global series
    global scareEnabled
    global scareTriggered
    if key == "KEY_FAVOURITE":
        # The emergency stop
        scareEnabled = False
        playIdleVideo()
    if key == "KEY_1":
        # enable scaring again
        series = 0
        scareEnabled = True
        scareTriggered = False
        playIdleVideo()
    if key == "KEY_2":
        # enable scaring again
        series = 1
        scareEnabled = True
        scareTriggered = False
        playIdleVideo()
    if key == "KEY_UP":
        playScaryVideo()
    if key == "KEY_DOWN":
        playIdleVideo()


def worker():
    for key in mode2ir.decodeSyvioKeys():
        print(key)
        handleKey(key)

t = threading.Thread(target=worker)
t.start()

# Main playback loop. Play the idle video back-to-back, unless
# it's scare time, in which case play one of the scary videos.
while True:
    try:
        print("loop")
        if idleLoop:
            playFile(videoSeries[series]["idleVideo"])
        else:
            scareVideos = videoSeries[series]["scareVideos"]
            videoIndex = random.randint(0, len(scareVideos) - 1)
            print("play video {0}".format(videoIndex))
            playFile(scareVideos[videoIndex])
        
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
    

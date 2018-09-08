import subprocess

# Key signatures obtained from a "SYVIO HDMI SWITCH" remote,
# using 'mode2 -s 500 -d /dev/lirc0',
syvioKeymap = {
    "_------------_________-_-___-_-_-_-_-_-_-___-_-___-___-___-___-___-___-_-___-___-_-_-_-_-_-___-_-_-___-___-___-___-___-_" : "KEY_1",
    "_------------_________-_-___-_-_-_-_-_-_-___-_-___-___-___-___-___-___-_-___-_-___-_-_-_-_-___-_-___-_-___-___-___-___-_" : "KEY_2",
    "_------------_________-_-___-_-_-_-_-_-_-___-_-___-___-___-___-___-___-_-___-___-___-_-_-_-_-___-_-_-_-___-___-___-___-_" : "KEY_3",
    "_------------_________-_-___-_-_-_-_-_-_-___-_-___-___-___-___-___-___-___-_-_-___-_-_-_-_-_-___-___-_-___-___-___-___-_" : "KEY_4",
    "_------------_________-_-___-_-_-_-_-_-_-___-_-___-___-___-___-___-___-___-_-___-___-_-_-_-_-_-___-_-_-___-___-___-___-_" : "KEY_5",
    "_------------_________-_-___-_-_-_-_-_-_-___-_-___-___-___-___-___-___-_-_-_-_-_-_-_-_-___-___-___-___-___-___-___-___-_" : "KEY_UP",
    "_------------_________-_-___-_-_-_-_-_-_-___-_-___-___-___-___-___-___-_-_-___-_-_-_-_-_-___-___-_-___-___-___-___-___-_" : "KEY_DOWN",
    "_------------_________-_-___-_-_-_-_-_-_-___-_-___-___-___-___-___-___-_-___-___-_-___-_-_-_-___-_-_-___-_-___-___-___-_" : "KEY_FAVOURITE",
}

syvioKeymapExtra = {
   "_------------____-_" : "REPEAT"
}

def stdoutLines(proc):
    while True:
        rawline = proc.stdout.readline()
        if rawline == '':
            return;
        yield rawline.decode("utf-8").strip()

def decodeLines(keymap, lines):
    for line in lines:
        if line in keymap:
            yield keymap[line]

def decodeKeys(keymap):
    while True:
        cmd = ["mode2", "-s", "500", "-d", "/dev/lirc0"]
        proc = subprocess.Popen(cmd, stdout = subprocess.PIPE)
        yield from decodeLines(keymap, stdoutLines(proc))

def decodeSyvioKeys():
    yield from decodeKeys(syvioKeymap)

if __name__ == "__main__":
    for key in decodeSyvioKeys():
        print(key)
        

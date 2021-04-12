#!/usr/bin/env python

import pyaudio
import wave
import sys
import time
import audioop
import os
import math
from threading import Thread
from pathlib import Path
import dothat.backlight as backlight
import dothat.lcd as lcd
import dothat.touch as nav
from dot3k.menu import Menu, MenuIcon, MenuOption

sys.path.append('.')
from plugins.clock import Clock
from plugins.graph import IPAddress, GraphTemp, GraphCPU, GraphNetSpeed
from plugins.text import Text
from plugins.utils import Backlight, Contrast
from plugins.wlan import Wlan


def getOutputFileName():
	offset = 0
	while True:
		offset = offset + 1
		output = "output" + str(offset) + ".wav"
		outputFile = Path(output)
		if not outputFile.is_file():
			return output

def recordAsync(args):
    chunk = 1024
    sample_format = pyaudio.paInt16
    channels = 2
    fs = 44100
    seconds = 3
    p = pyaudio.PyAudio()
    stopRecord = False

    print("Starting recording...")
    filename = getOutputFileName()
    print("Output = " + filename)
    stream = p.open(format=sample_format, channels=channels,rate=fs, frames_per_buffer=chunk,input=True)
    wf = wave.open(filename, "wb")
    wf.setnchannels(channels)
    wf.setsampwidth(p.get_sample_size(sample_format))
    wf.setframerate(fs)
    while True:
        data = stream.read(chunk)
        rms = audioop.rms(data, 2)		#our stereo rms, we want separate left and right though
        decibel = 20 * math.log10(rms)
        #print str(decibel)
        wf.writeframes(b''.join(data))

        if stopRecord == True:
            print("Stopping recording...")
            stream.close()
            wf.close()
            break

class Video(MenuOption):
    def __init__(self):
        self.enabled = True
        self._icons_setup = False
        MenuOption.__init__(self)

    def right(self):
        self.enabled = True
        self.update_enabled()
        return True

    def left(self):
        self.enabled = False
        self.update_enabled()
        return True

    def setup_icons(self, menu):
        menu.lcd.create_char(0, MenuIcon.arrow_left_right)
        self._icons_setup = True

    def cleanup(self):
        self._icons_setup = False

    def setup(self, config):
        self.config = config
        self.enabled = bool(self.get_option('Video', 'enabled', True))

    def update_enabled(self):
        self.set_option('Video', 'enabled', str(self.enabled))

    def redraw(self, menu):
        if not self._icons_setup:
            self.setup_icons(menu)

        menu.write_row(0, 'Video')
        menu.write_row(1, chr(0) + 'Enabled: ' + str(self.enabled))
        menu.clear_row(2)

class Performance(MenuOption):
    def __init__(self):
        self.isRecording = False
        MenuOption.__init__(self)

    def right(self):
        self.recordingThread = Thread(target=recordAsync, args=[0])
        self.recordingThread.start()
        self.isRecording = True
        self.update_status()

    def setup(self, config):
        self.config = config

    def update_status(self):
        self.set_option('Performance', 'recording', str(self.isRecording))

    def redraw(self, menu):
        menu.write_row(0, "Performance")
        if self.isRecording:
            menu.write_row(1, "Recording...")
        else:
            menu.write_row(1, "")
        menu.clear_row(2)

video = Video()
performance = Performance()

menu = Menu(
    structure={
        'Performance': performance,
        'Status': {
            'Wifi': Wlan(),
            'IP': IPAddress(),
            'CPU': GraphCPU(backlight),
            'Temp': GraphTemp(),
            'Clock': Clock(backlight)
        },
        'Settings': {
            'Display': {
                'Contrast': Contrast(lcd),
                'Backlight': Backlight(backlight)
            },
            'Video': video
        }
    },
    lcd=lcd,
    #idle_handler=my_invader,
    idle_timeout=30,
    input_handler=Text())
nav.bind_defaults(menu)
lcd.set_contrast(50)

while 1:
    menu.redraw()
    time.sleep(0.05)

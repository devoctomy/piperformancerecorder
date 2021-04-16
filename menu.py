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

class Audio(MenuOption):
    def __init__(self):
        self.inputDevices = []
        self.selectedInputDeviceIndex = -1
        self._icons_setup = False
        self.isRecording = False
        self.stopRecording = False
        self.p = pyaudio.PyAudio()
        self.enumerate_devices()
        MenuOption.__init__(self)

    def right(self):
        if self.selectedInputDeviceIndex < len(self.inputDevices) - 1:
            self.selectedInputDeviceIndex += 1
            self.update_selectedInputDeviceIndex()
            return True
        else:
            return False

    def left(self):
        if self.selectedInputDeviceIndex > -1:
            self.selectedInputDeviceIndex -= 1
            self.update_selectedInputDeviceIndex()
            return True
        else:
            return False

    def enumerate_devices(self):
        info = self.p.get_host_api_info_by_index(0)
        numdevices = info.get('deviceCount')
        for i in range (0,numdevices):
            if self.p.get_device_info_by_host_api_device_index(0,i).get('maxInputChannels')>0:
                self.inputDevices.append(self.p.get_device_info_by_host_api_device_index(0,i).get('name'))
        self.selectedInputDeviceIndex = self.p.get_device_info_by_index(1)

    def setup_icons(self, menu):
        menu.lcd.create_char(0, MenuIcon.arrow_left_right)
        self._icons_setup = True

    def cleanup(self):
        self._icons_setup = False
        self.p.terminate()

    def setup(self, config):
        self.config = config
        self.selectedInputDeviceIndex = bool(self.get_option('Audio', 'selectedInputDeviceIndex', -1))

    def update_selectedInputDeviceIndex(self):
        self.set_option('Audio', 'selectedInputDeviceIndex', self.selectedInputDeviceIndex)

    def redraw(self, menu):
        if not self._icons_setup:
            self.setup_icons(menu)

        menu.write_row(0, 'Audio')
        menu.write_row(1, chr(0) + 'In: ' + self.inputDevices[self.selectedInputDeviceIndex])
        menu.clear_row(2)

    def start_recording_async(self):
        if not self.isRecording:
            self.recordingThread = Thread(target=self.start_recording)
            self.recordingThread.start()

    def start_recording(self):
        chunk = 1024
        sample_format = pyaudio.paInt16
        channels = 2
        fs = 44100
        seconds = 3

        print("Starting recording...")
        filename = self.getOutputFileName()
        print("Output = " + filename)
        stream = self.p.open(input_device_index=self.selectedInputDeviceIndex, format=sample_format, channels=channels,rate=fs, frames_per_buffer=chunk,input=True)
        wf = wave.open(filename, "wb")
        wf.setnchannels(channels)
        wf.setsampwidth(self.p.get_sample_size(sample_format))
        wf.setframerate(fs)
        self.isRecording = True
        while True:
            data = stream.read(chunk)
            rms = audioop.rms(data, 2)              #our stereo rms, we want separate left and right though
            decibel = 20 * math.log10(rms)
            #print str(decibel)
            wf.writeframes(b''.join(data))

            if self.stopRecording:
                print("Stopping recording...")
                stream.close()
                wf.close()
                self.stopRecording = False
                break

    def getOutputFileName(self):
        offset = 0
        while True:
            offset = offset + 1
            output = "output" + str(offset) + ".wav"
            outputFile = Path(output)
            if not outputFile.is_file():
                return output


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
        audio.start_recording_async()
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

audio = Audio()
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
            'Audio': audio,
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

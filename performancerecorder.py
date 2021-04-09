import pyaudio
import wave
import time
import tty
import termios
import select
import sys
sys.path.append('../')
import audioop
import os
import math
import signal
import dothat.backlight as backlight
import dothat.lcd as lcd
import dothat.touch as nav
from UsbDetector import UsbDetector
from pathlib import Path

@nav.on(nav.UP)
def handle_up(ch, evt):
	lcd.clear();
	backlight.rgb(255, 0, 0)
	lcd.write("Up!")

@nav.on(nav.DOWN)
def handle_down(ch, evt):
	lcd.clear();
	backlight.rgb(0, 255, 0)	
	lcd.write("Down!")

@nav.on(nav.LEFT)
def handle_down(ch, evt):
        lcd.clear();
        backlight.rgb(0, 0, 255)
        lcd.write("Left!")

@nav.on(nav.RIGHT)
def handle_down(ch, evt):
        lcd.clear();
        backlight.rgb(255, 255, 0)
        lcd.write("Right!")

@nav.on(nav.BUTTON)
def handle_down(ch, evt):
        lcd.clear();
        backlight.rgb(0, 255, 255)
        lcd.write("Yes!")

@nav.on(nav.CANCEL)
def handle_down(ch, evt):
        lcd.clear();
        backlight.rgb(255, 0, 255)
        lcd.write("No!")

def getOutputFileName():
	offset = 0
	while True:
		offset = offset + 1
		output = "output" + str(offset) + ".wav"
		outputFile = Path(output)
		if not outputFile.is_file():
			return output

def isData():
	return select.select([sys.stdin], [], [], 0) == ([sys.stdin], [], [])

if __name__ == '__main__':
	usbDetector = UsbDetector()

	chunk = 1024
	sample_format = pyaudio.paInt16
	channels = 2
	fs = 44100
	seconds = 3
	p = pyaudio.PyAudio()

	old_settings = termios.tcgetattr(sys.stdin)
	try:
		tty.setcbreak(sys.stdin.fileno())
		record = False
		stopRecord = False

		while True:
			if isData():
				c = sys.stdin.read(1)
				if c == "r":
					record = True

			if record:
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

					if isData():
						c = sys.stdin.read(1)
						if c == "r":
							stopRecord = True
					if stopRecord == True:
						print("Stopping recording...")
						stream.close()
						wf.close()
						record = False
						stopRecord = False
						break


	finally:
		termios.tcsetattr(sys.stdin, termios.TCSADRAIN, old_settings)

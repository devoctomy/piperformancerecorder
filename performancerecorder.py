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
from UsbDetector import UsbDetector
from pathlib import Path

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

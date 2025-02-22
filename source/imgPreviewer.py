"""
imgPreviewer.py
	loads all the intermediary frames and displays specific frames called by the GIF output cutList
	requires OpenCV
pip install --upgrade opencv-python

"""

import json

filename = "cutFile.json"
outFile = open(filename, 'r')
print("cutFile opened as read-only")

tempDict:dict = json.load(outFile)
keyCheck = list(tempDict.keys())

# key: [startframe25, duration25, targetFrametime, cutType]

displayList = []

weldFrametime = 0.1 # weld a frame to last whole frame if partial frame is shorter than this in seconds

# frame counters for debug and editing purposes
frameCounter = 0
existingCutCounter = 0
weldedFrames = 0
partialFrames = 0

frametimeOverride ={
	0.05 : 0.06,
	0.06 : 0.08,
	0.07 : 0.08,
#	0.08 : 0.09,
	0.09 : 0.1,
	0.1  : 0.11,
	0.11 : 0.12,
	0.12 : 0.14,
	0.13 : 0.14,
	0.14 : 0.16,
#	0.15 : 0.16,
}

# read sequence: cutFile.json
for fileKeys in keyCheck:
	if "cut" in fileKeys:
		if tempDict[fileKeys][2] == "hold": # this is a single hold frame
			displayList.append([tempDict[fileKeys][0]*4 , round(tempDict[fileKeys][1]*0.04,2)]) # [100fps frame number , frame duration in seconds]
			frameCounter += 1
		else: # this is a section of multiple frames
			workingFrametime = tempDict[fileKeys][2] # get target frametime in key
			if workingFrametime in frametimeOverride: # if there is a frametime override specified earlier above
				# assign override frametime target
				workingFrametime = frametimeOverride[workingFrametime]
			
			# get starting frame and evaluate real time duration
			startFrame25 = tempDict[fileKeys][0] 
			realDuration = tempDict[fileKeys][1] *0.04

			# init loop
			countIndex = 0
			frameAdvance25 = workingFrametime * 25.0 # advance this number of cut frames (25fps) per loop

			while True: # for every export frame in this cut(in this case, just a preview)
				frameCounter += 1
				getFrame100 = int( round( (startFrame25 + (countIndex*frameAdvance25)) *4,0) )

				# check if next frame has enough remaining time to meet frametime limit 
				testRemainingDurationRatio = realDuration / workingFrametime
				if  testRemainingDurationRatio < 2.0: # there isn't enough
					if (testRemainingDurationRatio - 1.0 < 0.5) or (realDuration - workingFrametime < weldFrametime):
					# if last frame is less than half of target frametime or weldFramerate threshold
						# merge with this whole frame
						realDuration = round(realDuration,2) # round to nearest 0.01s
						displayList.append([getFrame100 , realDuration])
						weldedFrames += 1
					else:
						# make this whole frame and next partial frame now, and go to next cut
						displayList.append([getFrame100 , workingFrametime])
						frameCounter += 1
						getFrame100 = (countIndex + startFrame25)*4
						realDuration -= workingFrametime
						realDuration = round(realDuration,2) # round to nearest 0.01s
						displayList.append([getFrame100 , realDuration])
						partialFrames += 1
					break
				else:
					# make this whole frame and loop
					displayList.append([getFrame100 , workingFrametime])
				realDuration -= workingFrametime
				countIndex += 1
				continue

		# end of cut, go to next key
		existingCutCounter += 1

displayList.sort()

print(f"existing cuts in file: {existingCutCounter}")
print(f"existing output GIF frames: {frameCounter}")
print(f"welded GIF frames: {weldedFrames}")
print(f"partial GIF frames: {partialFrames}")



if input("start previewer? y/n : ") != 'y':
	print("invalid input. stopping...")
	exit()

# preview time: using openCV

import time

# openCV python library
# https://pypi.org/project/opencv-python/
import cv2 as ocv
	# pip install --upgrade opencv-python


# start loop
	# start timer
	# load image
	# display image
	# stop timer
	# wait for (frametime - timer - frametimeOvershot)
		# if overshot (i.e. negative number)
		# frametimeOvershot = -(negative number)
	# continue



# code based on: https://forum.opencv.org/t/load-image-sequence/3746/10

filepath = ".\\badapple_100fps\\badapple_%05d.png"

testFrameNumber = 1480 # test number from previous tests, actual number will be assigned in loop

print("startload....")
time01 = time.time()

imgSeq = ocv.VideoCapture(filepath)
assert imgSeq.isOpened()
	# loading my take some time on the first run, not quite sure why subsequent runs are faster

time02 = time.time()
deltaTime = int((time02 - time01) *1000)
print(f"==== load time elapsed: {deltaTime} ms")
print(f"==== number of frames loaded: {imgSeq.get(ocv.CAP_PROP_FRAME_COUNT)}")

ocv.namedWindow("badapplewindow", ocv.WINDOW_NORMAL)

for frame in displayList:
	timeframeStart = time.time()
		# it's a naiive implementation for preview purposes, i'll have to look up how to keep time profiling as accurate as possible
	
	testFrameNumber = frame[0] # get intermediary frame

	# setting read position and reading from there
		# https://stackoverflow.com/questions/33650974/opencv-python-read-specific-frame-using-videocapture
	imgSeq.set(ocv.CAP_PROP_POS_FRAMES, testFrameNumber)
	hasFrame, frameImg = imgSeq.read() # [return: t/f , data]

	# get elapsed seek time and evaluate frame display duration
	timeFrameEnd = time.time()
	thisFrameDuration = frame[1] - timeFrameEnd + timeframeStart

	if hasFrame:
		ocv.imshow("badapplewindow", frameImg)
		ocv.waitKey(int(thisFrameDuration*1000))
			# this NEEDS to follow after a read() command, so the image will draw on the window
			# https://stackoverflow.com/questions/22274789/cv2-imshow-function-is-opening-a-window-that-always-says-not-responding-pyth
			# https://docs.opencv.org/4.x/d7/dfc/group__highgui.html#ga453d42fe4cb60e5723281a89973ee563
	else:
		print("image display failed")
		break



print("end test, unloading....")
imgSeq.release()
ocv.destroyAllWindows()
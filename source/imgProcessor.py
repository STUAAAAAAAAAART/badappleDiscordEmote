"""
imgProcessor.py
	bakes intermediary frames to simplified GIF
"""


import math as m
import json

import os
import numpy as np

from PIL import Image as pim
from PIL import ImageDraw as pdr
from PIL import ImageChops as pch
	# pip install --upgrade pillow

filename = "cutFile.json"
outFile = open(filename, 'r')
print("cutFile opened as read-only")

print(os.getcwd())
# print(os.listdir())

"""
imgList = os.listdir("./badapple_100fps")
# NOTE: 100fps sequence, cuts are marked in 25fps, target frame"rate" is 12.5fps
print(len(imgList))
"""

sourceFolder = "badapple_100fps"
sourceFrameHeader = f"{sourceFolder}/badapple_"
	# "badapple_00000.png"

print("!!! DEBUG !!!")
print(sourceFrameHeader)

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

# test overrides in imgPreviewer.py!! 
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

thisSectionFrame100 = 0
nextSectionFrame100 = 0
frameTimeRoundingBin = 0.0
pushRoundingFrametime = 0.0

# read sequence: cutFile.json
for fileKeys in keyCheck:
	# write to displayList with [100fps frame number, 100fps frame end OR "hold", GIF frametime in seconds, frame blending type]

	if "cut" in fileKeys: # key: [startframe25, duration25, targetFrametime, cutType]
		thisSectionFrame100 = tempDict[fileKeys][0] *4
		nextSectionFrame100 = (tempDict[fileKeys][0] + tempDict[fileKeys][1]) *4
		thisSectionFrametime = tempDict[fileKeys][2]
		thisSectionBlendType = tempDict[fileKeys][3]
		
		if tempDict[fileKeys][2] == "hold": # this is a single hold frame
			holdFrameDuration = round(tempDict[fileKeys][1]*0.04 , 2) # seconds
			displayList.append( [
				thisSectionFrame100,
	 			"hold",
				holdFrameDuration,
		   		"none"
				]
			)
			frameCounter += 1
		else: # this is a section of multiple frames
			# prepare loop to make multiple GIF frames
			workingFrametime = tempDict[fileKeys][2] # get target frametime in key, seconds
			if workingFrametime in frametimeOverride: # if there is a frametime override specified earlier above
				# assign override frametime target
				workingFrametime = frametimeOverride[workingFrametime]
			
			# get starting frame and evaluate real time duration
			startFrame25 = tempDict[fileKeys][0] 
			realDuration = tempDict[fileKeys][1] *0.04 # seconds

			# init loop
			countIndex = 0
			frameAdvance25 = workingFrametime * 25.0 # advance this number of cut frames (25fps) per loop

			while True: # for every export frame in this cut(in this case, just a preview)
				frameCounter += 1
				getFrame100 = int( round( (startFrame25 + (countIndex * frameAdvance25)) *4,0) )
				nextFrame100 = int( round( (startFrame25 + ((countIndex +1) * frameAdvance25)) *4,0) )

				# check if next frame has enough remaining time to meet frametime limit 
				testRemainingDurationRatio = realDuration / workingFrametime
				if  testRemainingDurationRatio < 2.0: # there isn't enough
					# get rounding clipoffs
					roundDuration = round(realDuration, 2) # round to nearest 0.01s
					frameTimeRoundingBin += realDuration - roundDuration
					# if there's enough to make 0.01s, add it to the partials AFTER the partial frame evaluation later
					if frameTimeRoundingBin > 0.01:
						pushRoundingFrametime = 0.01
						frameTimeRoundingBin -= 0.01
					else:
						pushRoundingFrametime = 0.0

					if (testRemainingDurationRatio - 1.0 < 0.5) or (realDuration - workingFrametime < weldFrametime):
					# if last frame is less than half of target frametime or weldFramerate threshold
						# merge with this whole frame
						displayList.append([
							getFrame100,
							nextSectionFrame100,
							realDuration + pushRoundingFrametime, # whole frame + partial frame
							thisSectionBlendType
							])
						weldedFrames += 1
					else:
						# make this whole frame and next partial frame now, and go to next cut
						displayList.append([ # this whole frame
							getFrame100,
							nextFrame100,
							thisSectionFrametime, # whole frame
							thisSectionBlendType
							])
						frameCounter += 1
						getFrame100 = (countIndex + startFrame25)*4
						realDuration -= workingFrametime
						displayList.append([ # next partial frame
							getFrame100,
							nextSectionFrame100,
							realDuration + pushRoundingFrametime, # partial frame
							thisSectionBlendType
							]) 
						partialFrames += 1
					break
				else:
					# make this whole frame and loop
					displayList.append([
							getFrame100,
							nextFrame100,
							thisSectionFrametime,
							thisSectionBlendType
							])
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


if input("START PIL EXPORT? y/n : ") != 'y':
	print("invalid input. stopping...")
	exit()

def bakeAverage100(startFrame100:int = 0, endFrame100:int = 10, filenameHeader:str = "", fileExt:str = "png") -> pim.Image:
	"""averages pixels across multiple frames together

	edited from source: https://stackoverflow.com/a/17383621

	filename syntax in this function expects {header}{sequenceNumber}.{fileExtension}, e.g. "badapple_00000.png"

	loading images expects all of the same dimensions

	Inputs:
	startFrame100 : int
		int of first frame, note function automatically adds leading zeroes for 5 digits
	endFrame100 : int
		int +1 of last frame, or start of frame from next section (this is passed to range() )
	filenameHeader : str
		common {header} of image sequence, e.g. "badapple_" in "badapple_00000.png"
		relative paths also go here, e.g."./badapple_100fps/badapple_"
	fileExt : str
		name of file extension, without the dot
	"""
	if endFrame100 - startFrame100 < 2:
		raise ValueError(f"bakeAverage100(): not enough input frames ({endFrame100 - startFrame100 -1}); range input: {startFrame100} - {endFrame100}")
	
	# edited from source: https://stackoverflow.com/a/17383621

	# Access all PNG files in directory
	imlist = []
	for i in range(startFrame100, endFrame100):
		imlist.append(f"{sourceFrameHeader}{startFrame100:05d}.{fileExt}")

	# Assuming all images are the same size, get dimensions of first image
	w,h = pim.open(imlist[0]).size
	bakeFrameLength = len(imlist)

	# Create a numpy array of floats to store the average (assume RGB images)
	arr = np.zeros((h,w,3), float)

	# Build up average pixel intensities, casting each image as an array of floats
	for im in imlist:
		getFrameImg = pim.open(im)
		imarr = np.array(getFrameImg,dtype=float)
		arr=arr+imarr/bakeFrameLength
		getFrameImg.close()

	# Round values in array and cast as 8-bit integer
	arr = np.array(np.round(arr),dtype=np.uint8)

	# return final image
	return pim.fromarray(arr,mode="RGB")

def bakeAdd100(startFrame100:int = 0, endFrame100:int = 10, filenameHeader:str = "", fileExt:str = "png") -> pim.Image:
	"""adds pixel valuess across multiple frames together

	filename syntax in this function expects {header}{sequenceNumber}.{fileExtension}, e.g. "badapple_00000.png"

	loading images expects all of the same dimensions

	Inputs:
	startFrame100 : int
		int of first frame, note function automatically adds leading zeroes for 5 digits
	endFrame100 : int
		int +1 of last frame, or start of frame from next section (this is passed to range() )
	filenameHeader : str
		common {header} of image sequence
	fileExt : str
		name of file extension, without the dot
	"""
	if endFrame100 - startFrame100 < 2:
		raise ValueError(f"bakeAdd100(): not enough input frames ({endFrame100 - startFrame100 -1}); range input: {startFrame100} - {endFrame100}")
	
	imlist = []
	for i in range(startFrame100, endFrame100):
		imlist.append(f"{sourceFrameHeader}{startFrame100:05d}.{fileExt}")
	
	firstImg = pim.open(imlist.pop(0))
	bakeFrameImg = firstImg.copy()
	firstImg.close()
	for frameFile in imlist:
		loadImg = pim.open(frameFile)
		bakeFrameImg = pch.add(bakeFrameImg,loadImg)
		loadImg.close()
	return bakeFrameImg

def bakeMultiply100(startFrame100:int = 0, endFrame100:int = 10, filenameHeader:str = "", fileExt:str = "png") -> pim.Image:
	"""multiplies pixel valuess across multiple frames together

	filename syntax in this function expects {header}{sequenceNumber}.{fileExtension}, e.g. "badapple_00000.png"

	loading images expects all of the same dimensions

	Inputs:
	startFrame100 : int
		int of first frame, note function automatically adds leading zeroes for 5 digits
	endFrame100 : int
		int +1 of last frame, or start of frame from next section (this is passed to range() )
	filenameHeader : str
		common {header} of image sequence
	fileExt : str
		name of file extension, without the dot
	"""
	if endFrame100 - startFrame100 < 2:
		raise ValueError(f"bakeMultiply100(): not enough input frames ({endFrame100 - startFrame100 -1}); range input: {startFrame100} - {endFrame100}")
	
	imlist = []
	for i in range(startFrame100, endFrame100):
		imlist.append(f"{sourceFrameHeader}{startFrame100:05d}.{fileExt}")
	
	firstImg = pim.open(imlist.pop(0))
	bakeFrameImg = firstImg.copy()
	firstImg.close()
	for frameFile in imlist:
		loadImg = pim.open(frameFile)
		bakeFrameImg = pch.multiply(bakeFrameImg,loadImg)
		loadImg.close()
	return bakeFrameImg


# START BAKE
bakeCounter = 0
bakeTotal = len(displayList)

# return buckets
imgBucket = []
frametimeBucket = []

"""
PIL command for exporting images just for quick reference

pim.Image.save(outFileName, save_all=True, append_images=[im1, im2, ...], duration = [1.0, 0.01, ....], loop = 0)
pim.Image.save("badAppleBake.gif", save_all=True, imgBucket, frametimeBucket, loop = 0)

https://pillow.readthedocs.io/en/stable/handbook/image-file-formats.html#gif
https://pillow.readthedocs.io/en/stable/reference/ImagePalette.html#PIL.ImagePalette.ImagePalette
"""


for cutSection in displayList: # [100fps frame number, 100fps frame end OR "hold", GIF frametime in seconds, frame blending type]
	
	if cutSection[1] == "hold":
		# this is a hold frame, pass it over
		getImg100 = pim.open(f"{sourceFrameHeader}{cutSection[0]:05d}.png")
		imgBucket.append(getImg100.copy())
		frametimeBucket.append(cutSection[2])
		getImg100.close()
	else:
		# this is a section to merge multiple intermediary frames into single GIF frames
		bakeImg = None	
		if cutSection[3] == "add":
			bakeImg = bakeAdd100(cutSection[0], cutSection[1], sourceFrameHeader, "png")
		elif cutSection[3] == "multiply":
			bakeImg = bakeMultiply100(cutSection[0], cutSection[1], sourceFrameHeader, "png")
		elif cutSection[3] == "average":
			bakeImg = bakeAverage100(cutSection[0], cutSection[1], sourceFrameHeader, "png")
		else:
			# fallback, sample and pass frame untouched
			getImg100 = pim.open(f"{sourceFrameHeader}{cutSection[0]:05d}.png")
			bakeImg = getImg100.copy()
			getImg100.close()
		
		imgBucket.append(bakeImg)
		frametimeBucket.append(cutSection[2])
	
	bakeCounter += 1
	if bakeCounter % 125 == 0:
		print(f"progress: {bakeCounter} of {bakeTotal}")

print("bake complete. saving...")
# PIL.Image.save() requires frametimes to be in milliseconds.....
for i in range(len(frametimeBucket)):
	frametimeBucket[i] = frametimeBucket[i] * 1000

# pop first frame off bakelist
debugImgSaving = imgBucket.pop(0)
debugImgSaving.save(fp = "badAppleBake.gif", save_all = True, append_images = imgBucket, duration = frametimeBucket, loop = 0)

print("bake successful, cleaning up...")
for i in imgBucket:
	i.close()
debugImgSaving.close()




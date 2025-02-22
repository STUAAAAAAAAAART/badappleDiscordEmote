import math as m
import json

filename = "cutFile.json"
outFile = open(filename, 'r')
print("output file opened as read-only")

# check for existing cuts and offer continuing from file

tempDict:dict = json.load(outFile)
keyCheck = list(tempDict.keys())

frameCounter = 0
existingCutCounter = 0
for fileKeys in keyCheck:
	if "cut" in fileKeys:
		if tempDict[fileKeys][2] == "hold":
			frameCounter += 1
			#print(f"GIF frames in {fileKeys}: 1")
		else:
			frameCountingForGifHere = m.ceil(tempDict[fileKeys][1] *0.04 / tempDict[fileKeys][2] ) # duration / frametime = number of GIF frames
			frameCounter += frameCountingForGifHere
			#print(f"GIF frames in {fileKeys}: {frameCountingForGifHere}")
			#print(f"debug: {frameCounter}")
		existingCutCounter += 1

print(f"existing cuts in file: {existingCutCounter}")
print(f"existing output GIF frames: {frameCounter}")

outDict = {}
cutCounter = 0
previousCutEnd = 0

queryOverwrite = input("overwrite or add to this JSON file? o/a : ")

if queryOverwrite[0] in ['o','a']:
	if queryOverwrite[0] == 'a': # append
		outDict = tempDict.copy() # copy over dict (not make pointer)
		cutCounter = existingCutCounter # get last number of cuts
		previousCutEnd = tempDict[f"cut{existingCutCounter-1}"][0] + tempDict[f"cut{existingCutCounter-1}"][1] # get frame end of last cut
	else:
		frameCounter = 0 # reset frameCounter to 0 for new data
else:
	print("invalid input. stopping...")
	exit()

del(tempDict)
outFile.close()
print("output file closed")



textQueries = [
		"frame start",
		"frame end",
		"target frameTIME", # in multiples of 0.01s, or "hold"
		"cut type",
		"next? (y/n 1/0 empty/n)"
	]

outDict["__values"] = textQueries[:-1].copy()


isNext = True



print('enter "retry" at any point to redo an entry')
try:
	while isNext:
		isRetry = False
		printKey = [previousCutEnd]

		print("new cut")
		print(f"{textQueries[0]}: {previousCutEnd}")

		for useQuery in textQueries[1:]:
			userInput = input(f"{useQuery}: ")
			if userInput == "retry":
				isRetry = True
				print("inputs discarded, starting new cut again...")
				break
			else:
				printKey.append(userInput)

		# retry input for entire cut
		if isRetry:
			continue
		
		# cast numbers
		try:
			printKey[0] = int(printKey[0]) # start frame (25fps frame position)
		except:
			pass
		try:
			printKey[1] = int(printKey[1]) # end frame (25fps number of frames)
		except:
			pass
		try:
			printKey[2] = float(printKey[2]) # frametime (multiples of 0.01s)
		except:
			pass

		previousCutEnd =  printKey[1]
		# convert end frame to cut duration
		printKey[1] = printKey[1] - printKey[0] 
		# REMEMBER ZERO INDEX AND LAST FRAME IS -1 OF DURATION ON THE OTHER SIDE
		#	e.g. start 70 duration 30
		#	frame range 70-99
		print(f"frame duration: {printKey[1]}")

		if printKey[2] == "hold":
			frameCounter += 1
			print("frames added to GIF: 1")
		else:
			thisCut = m.ceil( printKey[1] *0.04 / printKey[2] )
			frameCounter += thisCut # 25fps -> real time -> frame total in frametime
			print(f"frames added to GIF: {thisCut}")
		print(f"number of frames in the GIF: {frameCounter}")

		if printKey[-1] == '': # no-input inputs return blank string
			pass
		elif printKey[-1][0] in ['n', 'N', 0]:
			isNext = False

		# append to dict
		#	remember to remove the last answer for going next
		outDict[f"cut{cutCounter}"] = printKey[:-1].copy()

		cutCounter += 1

		# next?
		if not isNext:
			break
except:
	print("\n!! input cancelled, saving file...")

print(f"number of frames in the GIF: {frameCounter}")
outDict["__frameCount"] = frameCounter

# save to file
fileData = json.dump(outDict, open(filename, 'w'), sort_keys=True, indent='\t', separators=(',', ': '))

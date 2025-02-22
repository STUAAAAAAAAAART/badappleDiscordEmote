import os

from PIL import Image as pim
from PIL import ImageDraw as pdr
from PIL import ImageChops as pch
	# pip install --upgrade pillow

print(os.getcwd())
# print(os.listdir())

sourceFolder = "./../source/badapple_100fps"

imgList = os.listdir(sourceFolder)
# NOTE: 100fps sequence, cuts are marked in 25fps, target frame"rate" is 12.5fps
print(len(imgList))

img1 = "badapple_04479.png"
img2 = "badapple_04495.png"

img1 = pim.open(f"{sourceFolder}/{img1}")
img2 = pim.open(f"{sourceFolder}/{img2}")

outImg = pch.add(img1,img2)


img1.close()
img2.close()

outImg.save("./testImageAdd.png", "png")

outImg.close()

import numpy
from PIL import Image

sourceFolder = "./../source/badapple_100fps"

# edited from source: https://stackoverflow.com/a/17383621

# Access all PNG files in directory

# imlist=[filename for filename in allfiles if  filename[-4:] in [".png",".PNG"]]
imlist = []

for i in range(4420,4440-1):
    imlist.append(f"{sourceFolder}/badapple_{i:05d}.png")


# Assuming all images are the same size, get dimensions of first image
w,h=Image.open(imlist[0]).size
N=len(imlist)

# Create a numpy array of floats to store the average (assume RGB images)
arr=numpy.zeros((h,w,3), float)

# Build up average pixel intensities, casting each image as an array of floats
for im in imlist:
    imarr=numpy.array(Image.open(im),dtype=float)
    arr=arr+imarr/N

# Round values in array and cast as 8-bit integer
arr=numpy.array(numpy.round(arr),dtype=numpy.uint8)

# Generate, save and preview final image
out=Image.fromarray(arr,mode="RGB")
out.save("./testImageAverage.png", "png")
#out.show()
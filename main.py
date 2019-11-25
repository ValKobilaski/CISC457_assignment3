# Image compression
#
# You'll need Python 2.7 and must install these packages:
#
#   scipy, numpy
#
# You can run this *only* on PNM images, which the netpbm library is used for.
#
# You can also display a PNM image using the netpbm library as, for example:
#
#   python netpbm.py images/cortex.pnm


import sys, os, math, time, netpbm
import numpy as np


# Text at the beginning of the compressed file, to identify it


headerText = 'my compressed image - v1.0'



# Compress an image


def compress( inputFile, outputFile ):

  # Read the input file into a numpy array of 8-bit values
  #
  # The img.shape is a 3-type with rows,columns,channels, where
  # channels is the number of component in each pixel.  The img.dtype
  # is 'uint8', meaning that each component is an 8-bit unsigned
  # integer.

  img = netpbm.imread( inputFile ).astype('uint8')
  
  # Compress the image
  #
  # REPLACE THIS WITH YOUR OWN CODE TO FILL THE 'outputBytes' ARRAY.
  #
  # Note that single-channel images will have a 'shape' with only two
  # components: the y dimensions and the x dimension.  So you will
  # have to detect this and set the number of channels accordingly.
  # Furthermore, single-channel images must be indexed as img[y,x]
  # instead of img[y,x,1].  You'll need two pieces of similar code:
  # one piece for the single-channel case and one piece for the
  # multi-channel case.

  startTime = time.time()
 
  outputBytes = bytearray()

  baseDict = {}

  for i in range(512):
    baseDict[str(i)] = i

  pixelValues = []

  if (len(img.shape) == 2):
    channels = 1
    for x in range(img.shape[0]):
      for y in range(img.shape[1]):
        pixelValues.append(img[x,y])
  
  elif (len(img.shape) == 3):
    channels = 3
    for x in range(img.shape[0]):
      for y in range(img.shape[1]):
        for c in range(img.shape[2]):
          pixelValues.append(img[x,y,c])
  else:
    print("invalid image format, exiting")
    quit()
  predictions = []
  predictions.append(pixelValues.pop(0) + 255)

  for i in pixelValues:
    predictions.append(int(pixelValues[i]) - int(pixelValues[i-1]) + 255)

    

  numSymbols = img.shape[0] * img.shape[1] * channels
  nextIndex = len(baseDict)

  s = ""

  for i in range(numSymbols):
    x = str(predictions[i])

    if s + x in baseDict:
      s = s + x

    else:
      outputBytes.append((int(baseDict[s]) >> 8) & 0xFF)
      outputBytes.append(int(baseDict[s]) & 0xFF)
    
      baseDict[s + x] = nextIndex
      nextIndex += 1
      s = x

  endTime = time.time()

  # Output the bytes
  #
  # Include the 'headerText' to identify the type of file.  Include
  # the rows, columns, channels so that the image shape can be
  # reconstructed.

  outputFile.write( '%s\n'       % headerText )
  if (channels == 1):
    outputFile.write( '%d %d\n' %(img.shape[0], img.shape[1]))
  else:
    outputFile.write( '%d %d %d\n' % (img.shape[0], img.shape[1], img.shape[2]))
  outputFile.write( outputBytes )

  # Print information about the compression
  
  inSize  = img.shape[0] * img.shape[1] * channels
  outSize = len(outputBytes)

  sys.stderr.write( 'Input size:         %d bytes\n' % inSize )
  sys.stderr.write( 'Output size:        %d bytes\n' % outSize )
  sys.stderr.write( 'Compression factor: %.2f\n' % (inSize/float(outSize)) )
  sys.stderr.write( 'Compression time:   %.2f seconds\n' % (endTime - startTime) )
  

# Uncompress an image

def uncompress( inputFile, outputFile ):

  # Check that it's a known file

  if inputFile.readline() != headerText + '\n':
    sys.stderr.write( "Input is not in the '%s' format.\n" % headerText )
    sys.exit(1)
    
  # Read the rows, columns, and channels.  
  line = []
  line = [int(x) for x in inputFile.readline().split()]
  rows = int(line[0])
  columns = int(line[1])

  if len(line) == 3:
    channels = 3
  else:
    channels = 1

  # Read the raw bytes.

  inputBytes = bytearray(inputFile.read())

  # Build the image
  #
  # REPLACE THIS WITH YOUR OWN CODE TO CONVERT THE 'inputBytes' ARRAY INTO AN IMAGE IN 'img'.

  startTime = time.time()

  img = np.empty( [rows,columns,channels], dtype=np.uint8 )

  baseDict = {}
  for i in range(512):
    baseDict[i] = str(i) + ','

  byteIterator = iter(inputBytes)

  fileValues = []
  for i in range(len(inputBytes) // 2 - 1):
    fileValues .append(int(byteIterator.next()<< 8) + int(byteIterator.next()))

  s = baseDict[fileValues.pop(0)]
  output = s

  nextIndex = len(baseDict)

  for val in fileValues:
    if val in baseDict:
      t = baseDict[val]
    else:
      t = s + s.split(',')[0] + ','
    output += t
    baseDict[nextIndex] = s + t.split(',')[0] + ','
    s = t
    nextIndex += 1

  output = output.split(',')
  output.pop(-1)
  for i in range(1,len(output)):
    output[i] += output[i-1]

  i = 0
  if(channels == 3):
    for num in output:
      x = i // (columns * channels ) % channels
      y = i // channels % columns
      c = i % channels
      img[x,y,c] = num
      i += 1
  else:
    for num in output: 
      x = i // columns
      y = i % columns
      img[x,y] = num
    endTime = time.time()

  # Output the image

  netpbm.imsave( outputFile, img )

  sys.stderr.write( 'Uncompression time: %.2f seconds\n' % (endTime - startTime) )

  

  
# The command line is 
#
#   main.py {flag} {input image filename} {output image filename}
#
# where {flag} is one of 'c' or 'u' for compress or uncompress and
# either filename can be '-' for standard input or standard output.


if len(sys.argv) < 4:
  sys.stderr.write( 'Usage: main.py c|u {input image filename} {output image filename}\n' )
  sys.exit(1)

# Get input file
 
if sys.argv[2] == '-':
  inputFile = sys.stdin
else:
  try:
    inputFile = open( sys.argv[2], 'rb' )
  except:
    sys.stderr.write( "Could not open input file '%s'.\n" % sys.argv[2] )
    sys.exit(1)

# Get output file

if sys.argv[3] == '-':
  outputFile = sys.stdout
else:
  try:
    outputFile = open( sys.argv[3], 'wb' )
  except:
    sys.stderr.write( "Could not open output file '%s'.\n" % sys.argv[3] )
    sys.exit(1)

# Run the algorithm

if sys.argv[1] == 'c':
  compress( inputFile, outputFile )
elif sys.argv[1] == 'u':
  uncompress( inputFile, outputFile )
else:
  sys.stderr.write( 'Usage: main.py c|u {input image filename} {output image filename}\n' )
  sys.exit(1)

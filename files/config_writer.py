from tracking.preprocessing.color_extractor import color_extractor
import cv2
import numpy as np
import sys
import arguments
import yaml
from pathlib import Path

# Arguments and Configuration --------------------------------------------------

parser = arguments.parser
argv = sys.argv[1:]
a = parser.parse_args( argv )
print( f"a: {a}")
project_path = Path( a.project_path )
config_file = project_path / a.config_file
print( f"config_file: {config_file}")

config = {}

with open( config_file, 'r' ) as f:
    config_tmp = yaml.safe_load(f)
    if config_tmp != None:
        config = config_tmp

video = {}
frame_delay = 1 # delay in milliseconds between frames, or 0 to wait indefinitely for keypress.
toggle = [1, 0]

# Set-up -----------------------------------------------------------------------

def stackImages(scale,imgArray):
    rows = len(imgArray)
    cols = len(imgArray[0])
    rowsAvailable = isinstance(imgArray[0], list)
    width = imgArray[0][0].shape[1]
    height = imgArray[0][0].shape[0]
    if rowsAvailable:
        for x in range ( 0, rows):
            for y in range(0, cols):
                if imgArray[x][y].shape[:2] == imgArray[0][0].shape [:2]:
                    imgArray[x][y] = cv2.resize(imgArray[x][y], (0, 0), None, scale, scale)
                else:
                    imgArray[x][y] = cv2.resize(imgArray[x][y], (imgArray[0][0].shape[1], imgArray[0][0].shape[0]), None, scale, scale)
                if len(imgArray[x][y].shape) == 2: imgArray[x][y]= cv2.cvtColor( imgArray[x][y], cv2.COLOR_GRAY2BGR)
        imageBlank = np.zeros((height, width, 3), np.uint8)
        hor = [imageBlank]*rows
        hor_con = [imageBlank]*rows
        for x in range(0, rows):
            hor[x] = np.hstack(imgArray[x])
        ver = np.vstack(hor)
    else:
        for x in range(0, rows):
            if imgArray[x].shape[:2] == imgArray[0].shape[:2]:
                imgArray[x] = cv2.resize(imgArray[x], (0, 0), None, scale, scale)
            else:
                imgArray[x] = cv2.resize(imgArray[x], (imgArray[0].shape[1], imgArray[0].shape[0]), None,scale, scale)
            if len(imgArray[x].shape) == 2: imgArray[x] = cv2.cvtColor(imgArray[x], cv2.COLOR_GRAY2BGR)
        hor= np.hstack(imgArray)
        ver = hor
    return ver

def empty(a):
    pass


## Get Color Range

print('Getting initial color range...')

if config:
    color_range = config['color_range']
else:
    color_range = color_extractor(a.video_file)

## Input Video file

cap = cv2.VideoCapture(a.video_file)
video['width']       = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
video['height']      = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
video['frame_rate']  = int(cap.get(cv2.CAP_PROP_FPS))
video['frame_count'] = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

config['video'] = video

## Video Read Loop

ret, frame = cap.read()

cv2.namedWindow('Stacked Images', cv2.WINDOW_NORMAL) # Create a named window
cv2.resizeWindow("Stacked Images", 1200, 700)
cv2.moveWindow("Stacked Images", 40, 30)              # Move it to (40,30)
cv2.createTrackbar("Hue Min","Stacked Images",color_range[0],179,empty)
cv2.createTrackbar("Hue Max","Stacked Images",color_range[3],179,empty)
cv2.createTrackbar("Sat Min","Stacked Images",color_range[1],255,empty)
cv2.createTrackbar("Sat Max","Stacked Images",color_range[4],255,empty)
cv2.createTrackbar("Val Min","Stacked Images",color_range[2],255,empty)
cv2.createTrackbar("Val Max","Stacked Images",color_range[5],255,empty)

key = None

while ret:

    # do stuff
    # 1. Get start frame
    # 2. Crop frame
    # 3. Get pattern ROI
    # 4. Get left and right hand ROI
    # 5. Get ball color range
    # 6. Get hand color range
    # 7. Get end frame

    image = frame

    while frame_delay == 0 and key != 27:
        imageHSV = cv2.cvtColor(image,cv2.COLOR_BGR2HSV)
        h_min = cv2.getTrackbarPos("Hue Min","Stacked Images")
        h_max = cv2.getTrackbarPos("Hue Max", "Stacked Images")
        s_min = cv2.getTrackbarPos("Sat Min", "Stacked Images")
        s_max = cv2.getTrackbarPos("Sat Max", "Stacked Images")
        v_min = cv2.getTrackbarPos("Val Min", "Stacked Images")
        v_max = cv2.getTrackbarPos("Val Max", "Stacked Images")
        color_range = [h_min,s_min,v_min,h_max,s_max,v_max]
        print(color_range)
        lower = np.array([h_min,s_min,v_min])
        upper = np.array([h_max,s_max,v_max])
        mask = cv2.inRange(imageHSV,lower,upper)
        imageResult = cv2.bitwise_and(image,image,mask=mask)

        imageStack = stackImages(0.33,([image,imageHSV],[mask,imageResult]))
        cv2.imshow("Stacked Images", imageStack)
        key = cv2.pollKey()
        if key == 27:
            break
        elif key == ord(' '):
            frame_delay = toggle[frame_delay]

    if key == 27:
        break

    key = cv2.waitKey(frame_delay)
    if key == ord(' '):
        frame_delay = toggle[frame_delay]
    elif key == ord('f'):
        frame_delay = 0

    imageHSV = cv2.cvtColor(image,cv2.COLOR_BGR2HSV)
    lower = np.array(color_range[:3])
    upper = np.array(color_range[3:])
    mask = cv2.inRange(imageHSV,lower,upper)
    imageResult = cv2.bitwise_and(image,image,mask=mask)
    imageStack = stackImages(0.33,([image,imageHSV],[mask,imageResult]))
    cv2.imshow("Stacked Images", imageStack)
    ret, frame = cap.read()

config['color_range'] = color_range

## Configuration file requirements
#  Site swaps array
#  tracking_systems array
#  color_range
#  table_field_names
#  evaluate each iteration
#  tracking_preprocessing
#  max_cuadrant_misses
#  Number of tries to test the period of a string
#  max period threshold
#  decimal round
#  save_data (1: Excel 2: mot16)
#  gt_dir (ground truth data dir)
#  tracking_dir (tracking data files)
#  dataset_dir (where to find video)
#  video_file_format
#  gt_file_format
#  tracking_file_format

with open( config_file, 'w' ) as f:
    yaml.dump(config, f)
cap.release()
cv2.destroyAllWindows()

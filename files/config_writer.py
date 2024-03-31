from tracking.preprocessing.color_extractor import color_extractor
import cv2
import numpy as np
import sys
import arguments
import yaml
from tools.stack_images import stackImages
from pathlib import Path

# Arguments and Configuration --------------------------------------------------

# TODO: A bunch of this could be moved into another module.

parser = arguments.parser
argv = sys.argv[1:]
a = parser.parse_args( argv )
print( f"a: {a}")
project_path = Path( a.project_path )
config_file = project_path / a.config_file
print( f"config_file: {config_file}")
if not config_file.exists:
    config_file.touch(mode=644)

config = {}

with open( config_file, 'r' ) as f:
    config_tmp = yaml.safe_load(f)
    if config_tmp != None:
        config = config_tmp

video = {}
siteswap = []
dataset_dir = None

def get_video_file_path( v, dataset_dir ):
    path = Path( v )
    if path.parent.samefile('.') and dataset_dir:
        return ( Path ( a.dataset_dir / path.name ) )
    return ( path )

# Load data from config.

#  Site swaps array -- DONE
#  tracking_systems array -- DONE
#  color_range -- DONE
#  dataset_dir (where to find video) -- DONE
#

if config:
    video = config['video']
    siteswap = config.get('siteswap')

if a.siteswap:
    config['siteswap'] = [ a.siteswap ]

if a.system:
    config['tracking_systems'] = [ a.system ]

config['save_dir'] = a.save_dir
config['output_path'] = a.output_path
config['visualize'] = a.visualize

video_file_path = get_video_file_path( a.video_file, a.dataset_dir )
video['video_source'] = video_file_path.name
video['dataset_dir'] = f"{video_file_path.parent}"

frame_delay = 1 # delay in milliseconds between frames, or 0 to wait indefinitely for keypress.
toggle = [1, 0]

# Set-up -----------------------------------------------------------------------

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

    # Use cv2.displayOverlay to display control options
    # 1. Set start frame
    # 2. Crop frame
    # 3. Get pattern ROI
    # 4. Get left and right hand ROI
    # 5. Get ball color range
    # 6. Get hand color range
    # 7. Set end frame

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

## Configuration from final_system.py

config['table_field_names'] = [
    "ss", "MOTP", "MOTA", "Presence",
    "Prediction", "System used", "Num misses (cuadrants)", "Works"
]

#  evaluate each iteration
config['evaluate'] = True

#  tracking_preprocessing
config['tracking_preprocessing'] = True

#  max quadrant misses
config['max_cuadrant_misses'] = 0.49

#  Number of tries to test the period of a string
config['ss_test_numbers'] = 5

#  max period threshold
config['max_perido_threshold'] = 1.5

#  decimal round
config['decimal_round'] = 3

#  save_data (1: Excel 2: mot16)
config['save_data'] = 2

#  gt_dir (ground truth data dir)
config['gt_dir'] = 'results/mot16/GroundTruth/'

#  tracking_dir (tracking data files)
config['tracking_dir'] = 'results/mot16/Tracking/'

#  video_file_format
config['video_file_format'] = 'ss{}_red2_AlejandroAlonso.mp4'

#  gt_file_format
config['gt_file_format'] = '{}_manual2.txt'

#  tracking_file_format
config['tracking_file_format'] = '{}_{}.txt'

with open( config_file, 'w' ) as f:
    yaml.dump(config, f)
cap.release()
cv2.destroyAllWindows()

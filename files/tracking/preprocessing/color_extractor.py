import cv2
import numpy as np
import colorsys
#import pdb

def get_center( contour ):
    M = cv2.moments(contour)
    return [ int(M["m10"] / M["m00"]), int(M["m01"] / M["m00"]) ]

# Get the most detected color and range from there
# Returns
#   minimum hue, minimum saturation, minimum value,
#   maximum hue, maximum saturation, maximum value
def color_extractor(source_path, min_contour_area=1000, h_range=2, sv_range1=75, sv_range2=175, size=5):
    #pdb.set_trace()
    cap = cv2.VideoCapture(source_path)

    # Object detection from stable camera
    object_detector = cv2.createBackgroundSubtractorMOG2(
                        history=100,
                        varThreshold=40)

    ret, frame = cap.read()
    color_dict = {}
    current_frame = 0
    while ret:
        mask = object_detector.apply(frame) # Basically the mask is to apply BackgroundSubstractor with 100 and 40 to the whole image (translation?)
        _, mask = cv2.threshold( mask, 254, 255, # The mask is passed -i through a gray threshold
                                    cv2.THRESH_BINARY )
        contours, _ = cv2.findContours( mask, # From the result of that mask the contours are extracted
                                        cv2.RETR_TREE,
                                        cv2.CHAIN_APPROX_SIMPLE )

        image = frame

        for c in contours:
            area = cv2.contourArea(c)
            if area > min_contour_area:
                # Approx is an approximate polygon from the contour, the higher the cte (0.05 in this case) the tighter it is
                approx = cv2.approxPolyDP(c,0.05*cv2.arcLength(c,True),True)
                # The length is the number of sides, we ask that the minimum be square
                if len(approx) > 4:
                    # Check if it is convex, so that it is more of a square type, because the hands often catch four sides but two inwards or similar (translation?)
                    if cv2.isContourConvex(approx):
                        center = get_center(c)
                        cx, cy = center
                        # Get the colors of the pixels in whatever region
                        for i in range(-size//2,size//2 + 1):
                            for j in range(-size//2,size//2 + 1):
                                (b,g,r) = image[cy+i, cx+j]
                                if (b,g,r) in color_dict:
                                    color_dict[(b,g,r)] += 1
                                else:
                                    color_dict[(b,g,r)] = 1
                

        ret, frame = cap.read()
        current_frame += 1

    #pdb.set_trace()
    # Gets the most repeated color and passes it to hsv
    (b,g,r) = max(color_dict, key=color_dict.get)
    (h, s, v) = colorsys.rgb_to_hsv(r,g,b)
    # colorsys hsv is 1,1,255 instead of 180, 255, 255
    (h,s,v) = (int(180*h), int(255*s), v)

    cap.release()
    s1 = min(s, sv_range1)
    s2 = max(s, sv_range2)
    v1 = min(v, sv_range1)
    v2 = max(v, sv_range2) 
    # h selects the color, gives some flexibility, s and v select tones/shades of that color, all are taken (a smaller range could be made)
    return h-h_range, s1, v1, h+h_range, s2, v2


# It makes a histogram with the h, s and v channels and from there it catches the peaks and the near areas according to the threshold. It does not work well
def color_extractor_test(source_path, min_contour_area=1000, index_umbral=0.6, size=5):
    cap = cv2.VideoCapture(source_path)

    # Object detection from stable camera
    object_detector = cv2.createBackgroundSubtractorMOG2(
                        history=100,
                        varThreshold=40)

    ret, frame = cap.read()
    color_dict = {}
    color_dict["h"] = []
    color_dict["s"] = []
    color_dict["v"] = []
    current_frame = 0
    while ret:
        mask = object_detector.apply(frame) # Basically the mask is to apply BackgroundSubstractor with 100 and 40 to the whole image (translation?)
        _, mask = cv2.threshold( mask, 254, 255, # The mask is passed -i through a gray threshold
                                    cv2.THRESH_BINARY )
        contours, _ = cv2.findContours( mask, # From the result of that mask the contours are extracted
                                        cv2.RETR_TREE,
                                        cv2.CHAIN_APPROX_SIMPLE )

        image = frame
        hsv_img = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)

        # REMOVE NEARBY CONTOURS TO KEEP YOUR HANDS OFF MOST OF THE TIME
        for c in contours:
            # print(f"to: {to}")
            area = cv2.contourArea(c)
            if area > min_contour_area:
                #cv2.drawContours(image, [c], -1, (0, 255, 0), 2)
                center = get_center(c)
                cx, cy = center
                # TAKE COLOR IN 5x5 pej (translation?)
                for i in range(-size//2,size//2 + 1):
                    for j in range(-size//2,size//2 + 1):
                        color = hsv_img[cy+i, cx+j]
                #cv2.circle(image, (cx, cy), 20, (0, 255, 0), -1)
                        color_dict["h"].append(color[0])
                        color_dict["s"].append(color[1])
                        color_dict["v"].append(color[2])

        ret, frame = cap.read()
        current_frame += 1

    canals = ["h", "s", "v"]
    res = {}
    for canal in canals:
        histogram, _ = np.histogram(
            color_dict[canal], bins=256, range=(0, 256)
        )
        peaks = np.where(histogram > index_umbral*histogram.max())[0]
        min_idx, max_idx = peaks[0], peaks[-1]
        res[canal] = (min_idx, max_idx)

    cap.release()

    return res["h"][0], res["s"][0], int(res["v"][0]), res["h"][1], res["s"][1], int(res["v"][1])

# Get the most detected color and range from there
def color_extractor_test2(source_path, min_contour_area=1000, h_range=2, sv_range1=75, sv_range2=175, size=5):
    cap = cv2.VideoCapture(source_path)

    # Object detection from stable camera
    object_detector = cv2.createBackgroundSubtractorMOG2(
                        history=100,
                        varThreshold=40)

    ret, frame = cap.read()
    color_dict = {}
    current_frame = 0
    total_b = 0
    total_g = 0
    total_r = 0
    while ret:
        mask = object_detector.apply(frame) # Basically the mask is to apply BackgroundSubstractor with 100 and 40 to the whole image (translation?)
        _, mask = cv2.threshold( mask, 254, 255, # The mask is passed -i through a gray threshold
                                    cv2.THRESH_BINARY )
        contours, _ = cv2.findContours( mask, # From the result of that mask the contours are extracted
                                        cv2.RETR_TREE,
                                        cv2.CHAIN_APPROX_SIMPLE )

        image = frame

        for c in contours:
            area = cv2.contourArea(c)
            if area > min_contour_area:
                # Approx is an approximate polygon from the contour, the higher the cte (0.05 in this case) the tighter it is
                approx = cv2.approxPolyDP(c,0.05*cv2.arcLength(c,True),True)
                # The length is the number of sides, we ask that the minimum be square
                if len(approx) > 4:
                    # Check if it is convex, so that it is more of a square type, because the hands often catch four sides but two inwards or similar (translation?)
                    if cv2.isContourConvex(approx):
                        center = get_center(c)
                        cx, cy = center
                        # Get the colors of the pixels in whatever region
                        for i in range(-size//2,size//2 + 1):
                            for j in range(-size//2,size//2 + 1):
                                (b,g,r) = image[cy+i, cx+j]
                                total_b += b
                                total_g += g
                                total_r += r
                

        ret, frame = cap.read()
        current_frame += 1

    # Gets the most repeated color and passes it to hsv
    (b,g,r) = total_b//(current_frame*25), total_g//(current_frame*25), total_r//(current_frame*25)
    (h, s, v) = colorsys.rgb_to_hsv(r,g,b)
    # colorsys hsv is 1,1,255 instead of 180, 255, 255
    (h,s,v) = (int(180*h), int(255*s), v)

    cap.release()
    s1 = min(s, sv_range1)
    s2 = max(s, sv_range2)
    v1 = min(v, sv_range1)
    v2 = max(v, sv_range2) 
    # h selects the color, gives some flexibility, s and v select tones/shades of that color, all are taken (a smaller range could be made)
    return h-h_range, s1, v1, h+h_range, s2, v2

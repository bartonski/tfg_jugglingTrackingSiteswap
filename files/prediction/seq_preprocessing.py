import cv2
import numpy as np
import matplotlib.pyplot as plt
import math
from scipy.ndimage import gaussian_filter1d
from scipy.signal import argrelextrema

def contours_non_max_suppression(contours, threshold_value, use_distance=True):
    contours = sorted(contours, key=cv2.contourArea, reverse=True)

    overlaps = set()

    # Use the threshold as a distance, then remove smaller regions that are too close
    if use_distance:
        for i in range(len(contours)):
            for j in range(i+1, len(contours)):
                point1 = contour_center(contours[i])
                point2 = contour_center(contours[j])
                dist = np.linalg.norm(np.array(point1) - np.array(point2))
                if dist < threshold_value:
                    overlaps.add(j)
    # Use the threshold to check for intersection, thus removing regions that overlap too much
    else:
        for i in range(len(contours)):
            for j in range(i+1, len(contours)):
                # Draw rectangles that define each contour 
                (x1,y1,w1,h1) = cv2.boundingRect(contours[i])
                (x2,y2,w2,h2) = cv2.boundingRect(contours[j])
                a = (x1, y1)
                b = (x1+w1, y1+h1)
                c = (x2, y2)
                d = (x2+w2, y2+h2)
                width = min(b[0], d[0]) - max(a[0], c[0])
                height = min(b[1], d[1]) - max(a[1], c[1])
                # If there is any intersection
                if min(width,height) > 0:
                    intersection = width*height
                    area1 = (b[0]-a[0])*(b[1]-a[1])
                    area2 = (d[0]-c[0])*(d[1]-c[1])
                    union = area1 + area2 - intersection
                    # If the intersection is large enough, mark it as an overlap
                    overlap=intersection/union
                    if overlap > threshold_value:
                        overlaps.add(j)
        
    contours = [x for i, x in enumerate(contours) if i not in overlaps]

    return contours

def contour_center(c):
    M = cv2.moments(c)
    try: center = int(M['m10']/M['m00']), int(M['m01']/M['m00'])
    except: center = 0,0
    return center


def fill_contours(contours):
    filled_contours = []

    for contour in contours:
        # Get the filled outline as a list of points
        filled_contour = cv2.approxPolyDP(contour, 3, True)

        # Add the start point to the end of the list to close the contour
        filled_contour = np.concatenate((filled_contour, filled_contour[0].reshape(1, -1)))

        # Add the filled outline to the list of filled outlines
        filled_contours.append(filled_contour)

    return filled_contours


def point_extractor(source_path, min_contour_area=2500, x_mul_threshold=0.6, y_mul_threshold=0.21, visualize=False):
    cap = cv2.VideoCapture(source_path)

    # Object detection from stable camera
    object_detector = cv2.createBackgroundSubtractorMOG2(
                        history=100,
                        varThreshold=10)

    if visualize:
        cv2.namedWindow('img', cv2.WINDOW_NORMAL)

    ret, img = cap.read()
    hist = None

    max_x, max_y = cap.get(cv2.CAP_PROP_FRAME_WIDTH), cap.get(cv2.CAP_PROP_FRAME_HEIGHT)
    bins = (int(max_x), int(max_y))
    hist_range = [(0, max_x), (0, max_y)]

    num_frames = 0
    while ret:
        if visualize:
            img_copy = img.copy()

        mask = object_detector.apply(img) # Basically the mask is to apply BackgroundSubstractor with 100 and 40 to the whole image (translation?)

        _, mask = cv2.threshold( mask, 254, 255, # The mask is passed -i through a gray threshold
                                    cv2.THRESH_BINARY )
        contours, _ = cv2.findContours( mask, # From the result of that mask the contours are extracted
                                        cv2.RETR_TREE,
                                        cv2.CHAIN_APPROX_SIMPLE )
        true_contours = []
        for c in contours:
            area = cv2.contourArea(c)
            if area > min_contour_area:
                true_contours.append(c)
        true_contours = contours_non_max_suppression(true_contours, 39)
        coords = []
        for cnt in true_contours:
            if visualize:
                cv2.drawContours(img_copy, [cnt], 0, (0, 0, 255), 2)
            mask = np.zeros_like(img)
            cv2.fillPoly(mask, [cnt], 255)
            pts = np.where(mask == 255)
            for i in range(len(pts[0])):
                coords.append((pts[1][i], pts[0][i]))
                if visualize:
                    x1, y1 = pts[1][i], pts[0][i]
                    cv2.circle(img_copy, (x1, y1), 0, (0, 0, 255), 2)

        if len(coords) > 0:
            x_coords, y_coords = zip(*coords)
    
            hist_frame, xedges, yedges = np.histogram2d(x_coords, y_coords, bins=bins, range=hist_range)
            if hist is None:
                hist = hist_frame
            else:
                hist += hist_frame   

        if visualize:
            cv2.imshow('img', img_copy)
            #cv2.imshow('img', cv2.resize(img, (480,700)))
            k=cv2.waitKey(1)
            if k==27: break
        ret, img = cap.read()

        num_frames += 1 

    # The point on the x-axis is obtained where the two detection clusters separate
    column_sums = np.sum(hist, axis=1)
    smooth = gaussian_filter1d(column_sums, 10)
    x_range = np.where(smooth > (0.2 * np.max(smooth)))[0]
    interval = smooth[x_range[0]:x_range[-1]]
    local_mins = argrelextrema(interval, np.less)
    if len(local_mins[0]) == 0:
        x_mid_point = max_x//2
    else:
        x_mid_point = np.where(smooth == np.min(smooth[local_mins+x_range[0]]))[0][0]

    # The point of the y-axis that marks the upper zone of the clusters is obtained.
    row_sums = np.sum(hist, axis=0)
    threshold = row_sums.max()*y_mul_threshold
    y_mid_point = 0
    for i, value in enumerate(row_sums):
        if value >= threshold:
            y_mid_point = i
            break
    y_mid_point = hist_range[1][1]- y_mid_point

    if visualize:
        cap.release()
        cv2.destroyAllWindows()

    """ plt.imshow(hist.T, origin='upper', extent=[xedges[0], xedges[-1], yedges[0], yedges[-1]])
    plt.axvline(x=x_mid_point, color='r', linestyle='--')
    plt.axhline(y=y_mid_point, color='r', linestyle='--')
    plt.colorbar()
    plt.title('Mapa de calor del movimiento en el video')
    plt.show() """

    return int(x_mid_point), int(max_y-y_mid_point) # The subtraction to put the 0,0 top left


if __name__ == "__main__":
    source_path = './dataset/tanda2/ss7corto_red2_AlejandroAlonso.mp4'
    #source_path = './dataset/jugglingLab/ss4_red_JugglingLab.mp4'
    print(point_extractor(source_path, visualize=False, min_contour_area=3000))
    # TODO limit time, for example the middle 10 seconds or something like that

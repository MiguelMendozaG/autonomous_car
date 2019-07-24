import numpy as np
import time
import math
import cv2 as cv
#from matplotlib import pyplot as plt
import numpy as np



def region_of_interest(edges):
    height, width = edges.shape
    mask = np.zeros_like(edges)

    # only focus bottom half of the screen
    polygon = np.array([[
        (0, height * 1 / 2),
        (width, height * 1 / 2),
        (width, height),
        (0, height),
    ]], np.int32)

    cv.fillPoly(mask, polygon, 255)
    cropped_edges = cv.bitwise_and(edges, mask)
    return cropped_edges


def detect_line_segments(cropped_edges):
    # tuning min_threshold, minLineLength, maxLineGap is a trial and error process by hand
    rho = 1  # distance precision in pixel, i.e. 1 pixel
    angle = np.pi / 180  # angular precision in radian, i.e. 1 degree
    min_threshold = 10  # minimal of votes
    line_segments = cv.HoughLinesP(cropped_edges, rho, angle, min_threshold, 
                                    np.array([]), minLineLength=8, maxLineGap=4)

    return line_segments


def make_points(frame, line):
    height, width, _ = frame.shape
    slope, intercept = line
    y1 = height  # bottom of the frame
    y2 = int(y1 * 1 / 2)  # make points from middle of the frame down

    # bound the coordinates within the frame
    x1 = max(-width, min(2 * width, int((y1 - intercept) / slope)))
    x2 = max(-width, min(2 * width, int((y2 - intercept) / slope)))
    return [[x1, y1, x2, y2]]

def average_slope_intercept(frame, line_segments):
    """
    This function combines line segments into one or two lane lines
    If all line slopes are < 0: then we only have detected left lane
    If all line slopes are > 0: then we only have detected right lane
    """
    lane_lines = []
    if line_segments is None:
        print('No line_segment segments detected')
        return False

    height, width, _ = frame.shape
    left_fit = []
    right_fit = []

    boundary = 1/3
    left_region_boundary = width * (1 - boundary)  # left lane line segment should be on left 2/3 of the screen
    right_region_boundary = width * boundary # right lane line segment should be on left 2/3 of the screen

    for line_segment in line_segments:
        for x1, y1, x2, y2 in line_segment:
            if x1 == x2:
                #print('skipping vertical line segment (slope=inf): %s' % line_segment)
                continue
            fit = np.polyfit((x1, x2), (y1, y2), 1)
            slope = fit[0]
            intercept = fit[1]
            if slope < 0:
                if x1 < left_region_boundary and x2 < left_region_boundary:
                    left_fit.append((slope, intercept))
            else:
                if x1 > right_region_boundary and x2 > right_region_boundary:
                    right_fit.append((slope, intercept))

    left_fit_average = np.average(left_fit, axis=0)
    if len(left_fit) > 0:
        lane_lines.append(make_points(frame, left_fit_average))

    right_fit_average = np.average(right_fit, axis=0)
    if len(right_fit) > 0:
        lane_lines.append(make_points(frame, right_fit_average))

    return lane_lines


def display_lines(frame, lines, line_color=(0, 255, 0), line_width=2):
    line_image = np.zeros_like(frame)
    if lines is not None:
        for line in lines:
            for x1, y1, x2, y2 in line:  
                cv.line(frame, (x1, y1), (x2, y2), line_color, line_width)
                print (x1, y1, x2, y2)
    #plt.imshow(frame)
    #line_image = cv.addWeighted(frame, 0.8, line_image, 1, 1)
    return frame


#display_image = display_lines(raw_image, lane_lines_image)
#plt.imshow(display_image)


def slopes(lines):
  if lines is not None:
        m = []
        for line in lines:
            for x1, y1, x2, y2 in line:
                #print ("x1: ", x1,", y1: ", y1, ", x2: ", x2, ", y2: ", y2)
                slope_1 = (y2 - y1) / (x2- x1)
                m.append(slope_1)  
  return m


def middle_line(frame, lane_lines):

    if len(lane_lines) == 0:
        return 0,0,0,0

    height, width, _ = frame.shape
    if len(lane_lines) == 1:
        x1, _, x2, _ = lane_lines[0][0]
        x_offset = x2 - x1
    else:
        _, _, left_x2, _ = lane_lines[0][0]
        _, _, right_x2, _ = lane_lines[1][0]
        camera_mid_offset_percent = 0.02 # 0.0 means car pointing to center, -0.03: car is centered to left, +0.03 means car pointing to right
        ##mid = int(width / 2 * (1 + camera_mid_offset_percent))
        mid = int(width / 2 )
        x_offset = (left_x2 + right_x2) / 2 #- mid
        
    x_offset = int(x_offset)
    y_offset = int(height / 2)
    x_init = int(width / 2)
    y_init = int(height)
    
    
    
    return x_offset, y_offset, x_init, y_init


def add_central_line(frame, lines, line_color=(0, 0, 255), line_width=2):
    line_image = np.zeros_like(frame)
    x1, y1, x2, y2 = lines
    if lines is not None:
          cv.line(frame, (x1, y1), (x2, y2), line_color, line_width)
          print (x1, y1, x2, y2)
    #plt.imshow(frame)
    #line_image = cv.addWeighted(frame, 0.8, line_image, 1, 1)
    return frame

def get_output_angle(image, x1,y1,x2,y2 = 123456789):
    if (y2 == 123456789):
      return False
    else:
      num = y2 - y1
      den = x1 - x2
      if den == 0:
        return 90
      degrees = math.degrees(math.atan(num / den))
      return degrees



def input_output(image):
	start = time.time()
	raw_image = np.array(image)
	status = cv.imwrite('output_raw.png', raw_image)
	hsv_image = cv.cvtColor(raw_image, cv.COLOR_RGB2HSV)
	status2 = cv.imwrite('output_hsv.png', hsv_image)
	#plt.imshow(hsv_image)


	lower_blue = np.array([60, 40, 40])
	upper_blue = np.array([150, 255, 255])
	mask = cv.inRange(hsv_image, lower_blue, upper_blue)
	#plt.imshow(mask)

	edges = cv.Canny(mask, 200, 400)
	#plt.imshow(edges)

	croped_image = region_of_interest(edges)
	#plt.imshow(croped_image)

	lines_segments_image = detect_line_segments(croped_image)
	#print(lines_segments_image)


	lane_lines_image = average_slope_intercept(raw_image, lines_segments_image)
	if (lane_lines_image == False):
		return False
	else:
		slopes_image = slopes(lane_lines_image)
		print (slopes_image)


		line_offset = middle_line(raw_image, lane_lines_image)
		print ("line offset", line_offset)


		degrees = get_output_angle (line_offset[0], line_offset[1] , line_offset[2], line_offset[3])
		if (degrees == False):
		   print ("Degrees are false")
		else:
		   end = time.time()
		   print (end - start)
		   print (degrees)
		   return degrees

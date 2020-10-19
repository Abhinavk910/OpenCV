import cv2
import imutils
import numpy as np

def birdeyeview(image):
    image2 = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    image2 = cv2.bilateralFilter(image2,11,17,17)
    image2 = cv2.Canny(image2, 30, 200)

    cnts = cv2.findContours(image2, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    cnts = imutils.grab_contours(cnts)
    cnts = sorted(cnts, key = cv2.contourArea, reverse = True)[:10]
    screencnt = None
    check = True
    for cnt in cnts:
        peri = cv2.arcLength(cnt, True)
        approx = cv2.approxPolyDP(cnt, 0.015*peri, True)

        if len(approx) == 4:
            check = False
            screencnt = approx
            break
    if check:
        return 'did not detect'
    else:
        pts = screencnt.reshape(4, 2)
        rect = np.zeros((4, 2), dtype = "float32")

        # the top-left point has the smallest sum whereas the bottom-right has the largest sum
        s = pts.sum(axis = 1)
        rect[0] = pts[np.argmin(s)]
        rect[2] = pts[np.argmax(s)]


        # compute the difference between the points -- the top-right will have the minumum difference and the bottom-left will
        # have the maximum difference
        diff = np.diff(pts, axis = 1)
        rect[1] = pts[np.argmin(diff)]
        rect[3] = pts[np.argmax(diff)]

        ratio = image.shape[0] / 300.0
        rect2 = rect*ratio

        (tl, tr, br, bl) = rect
        widthA = np.sqrt(((br[0] - bl[0]) ** 2) + ((br[1] - bl[1]) ** 2))
        widthB = np.sqrt(((tr[0] - tl[0]) ** 2) + ((tr[1] - tl[1]) ** 2))
        # ...and now for the height of our new image
        heightA = np.sqrt(((tr[0] - br[0]) ** 2) + ((tr[1] - br[1]) ** 2))
        heightB = np.sqrt(((tl[0] - bl[0]) ** 2) + ((tl[1] - bl[1]) ** 2))
        # take the maximum of the width and height values to reach
        # our final dimensions
        maxWidth = max(int(widthA), int(widthB))
        maxHeight = max(int(heightA), int(heightB))
        # construct our destination points which will be used to map the screen to a top-down, "birds eye" view
        dst = np.array([[0, 0],
            [maxWidth - 1, 0],
            [maxWidth - 1, maxHeight - 1],
            [0, maxHeight - 1]], dtype = "float32")
        # calculate the perspective transform matrix and warp  the perspective to grab the screen
        M = cv2.getPerspectiveTransform(rect, dst)
        warp = cv2.warpPerspective(image, M, (maxWidth, maxHeight))
        return warp

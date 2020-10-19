import cv2
import os
import imutils
from imutils import contours
import numpy as np
from scipy import stats
import itertools
from tensorflow.keras.preprocessing.image import img_to_array
from tensorflow.keras.models import load_model
from all_projects.opencv.project_sudoku_solver.birdeyeview import birdeyeview
import warnings
warnings.filterwarnings('ignore')
warnings.resetwarnings()

def findNextCellToFill(grid, i, j):
        for x in range(i,9):
                for y in range(j,9):
                        if grid[x][y] == 0:
                                return x,y
        for x in range(0,9):
                for y in range(0,9):
                        if grid[x][y] == 0:
                                return x,y
        return -1,-1

def isValid(grid, i, j, e):
        rowOk = all([e != grid[i][x] for x in range(9)])
        if rowOk:
                columnOk = all([e != grid[x][j] for x in range(9)])
                if columnOk:
                        # finding the top left x,y co-ordinates of the section containing the i,j cell
                        secTopX, secTopY = 3 *(i//3), 3 *(j//3) #floored quotient should be used here.
                        for x in range(secTopX, secTopX+3):
                                for y in range(secTopY, secTopY+3):
                                        if grid[x][y] == e:
                                                return False
                        return True
        return False

def solveSudoku(grid, i=0, j=0):
        i,j = findNextCellToFill(grid, i, j)
        if i == -1:
                return True
        for e in range(1,10):
                if isValid(grid,i,j,e):
                        grid[i][j] = e
                        if solveSudoku(grid, i, j):
                                return True
  
                        grid[i][j] = 0
        return False

def solve_sudoku(image_numpy, beyeview=False, box_h=(45, 55), digit_h=(20, 45), digit_w=(9, 30)):


    box_h_low, box_h_high = box_h
    digit_h_low, digit_h_high = digit_h
    digit_w_low, digit_w_high = digit_w

    if beyeview:
        image = birdeyeview(imutils.resize(image_numpy, width=500))
    else:
        image = image_numpy.copy()

    image = imutils.resize(image,  width = 500)
    output_image = image.copy()
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    gray = cv2.bitwise_not(gray)
    gray = cv2.threshold(gray, 20, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)[1]

    refCnts = cv2.findContours(
        gray.copy(), cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
    refCnts = imutils.grab_contours(refCnts)
    refCnts = contours.sort_contours(refCnts, method="left-to-right")[0]

    locs = []
    locsgrid = []
    for (i, c) in enumerate(refCnts):

        (x, y, w, h) = cv2.boundingRect(c)

        if box_h_low < h < box_h_high and box_h_low < w < box_h_high:
            locsgrid.append((x, y, w, h))
            cv2.rectangle(image, (x, y), (x+w, y+h), (0, 0, 255), 2)
            continue
        if digit_h_low < h < digit_h_high and digit_w_low < w < digit_w_high:
            locs.append((x, y, w, h))
            cv2.rectangle(image, (x, y), (x+w, y+h), (100, 255, 0), 2)



    if len(locsgrid) < 5:
        kernel = np.ones((3, 3), np.uint8)
        img_dilation = cv2.dilate(gray, kernel, iterations=4)
        img_dilation = cv2.erode(img_dilation, kernel, iterations=2)

        refCnts = cv2.findContours(
            img_dilation, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
        refCnts = imutils.grab_contours(refCnts)
        refCnts = contours.sort_contours(refCnts, method="left-to-right")[0]

        locsgrid = []
        for (i, c) in enumerate(refCnts):

            (x, y, w, h) = cv2.boundingRect(c)

            if box_h_low < h < box_h_high and box_h_low < w < box_h_high:
                locsgrid.append((x, y, w, h))
                continue


    locs = sorted(locs, key=lambda k: [k[1], k[0]])
    return image, locsgrid, locs, gray, output_image


def compute(locsgrid, locs, gray, output_image):

    model = load_model("all_projects/opencv/project_sudoku_solver/assets/sudokunew6.h5")
    con = 2

    mode_x = int(stats.mode([i[0] for i in locsgrid])[0])+con

    mode_y = int(stats.mode([i[1] for i in locsgrid])[0])+con


    mode_width = int(stats.mode([i[2] for i in locsgrid])[0])+con

    mode_height = int(stats.mode([i[3] for i in locsgrid])[0])+con


    xx = sorted([i for i in range(mode_x + mode_width,  525, mode_width)
                 ] + [i for i in range(mode_x, -20, - mode_width)])[:-1]
    yy = sorted([i for i in range(mode_y + mode_height, 525, mode_height)
                 ] + [i for i in range(mode_y, -20, - mode_height)])[:-1]

    locsgrid = np.array(list(itertools.product(xx, yy)))

    new = []
    b = np.array([mode_width, mode_height])
    for i in range(0, len(locsgrid)):
        new.append(np.concatenate([locsgrid[i], b]))

    def calposition(vvx, vvy, w, h, xx, yy):
        cx = vvx + w/2
        cy = vvy + h/2
        x = None
        y = None
        for j, i in enumerate(xx):
            if cx < i and x == None:
                x = j
                break
        for j, i in enumerate(yy):
            if cy < i and y == None:
                y = j
        return (x, y)

    def sortgrid(new):

        sort = sorted(new, key=lambda k: [k[1], k[0]])
        xx = [i*sort[0][2]+sort[0][0] for i in range(1, 10)]
        yy = [i*sort[0][3]+sort[0][1] for i in range(1, 10)]
        return (sort, xx, yy)

    sort, xx, yy = sortgrid(new)
    new2 = []
    for (x1, y1, w1, h1) in sort:
        i = None
        for (x2, y2, w2, h2) in locs:
            cx = x2 + w2/2
            cy = y2 + h2/2
            if x1 < cx < x1+w1:
                if y1 < cy < y1+h1:

                    i, j = calposition(x2, y2, w2, h2, xx, yy)
                    new2.append([x1, y1, w1, h1, x2, y2, w2, h2, i, j])
                    break
        if i == None:
            new2.append([x1, y1, w1, h1])

    output = []
    label_output = []

    grid = np.zeros((9, 9))
    for (i, detail) in enumerate(new2):
        if len(detail) == 10:
            (_, _, _, _, x, y, w, h, ix, jy) = detail
            roi = gray[y:y + h+5, x:x + w+3]
            image2 = cv2.resize(roi, (28, 28))
            image2 = image2.astype("float") / 255.0
            image2 = img_to_array(image2)
            image2 = np.expand_dims(image2, axis=0)
            prediction = model.predict(image2)[0]
            label = np.argmax(prediction)
            if prediction[label] < 0.5:
                label = 0
            grid[jy, ix] = label
            label_output.append(label)


    solveSudoku(grid)

    for i, j in enumerate(new2):
        if len(j) != 10:
            x = i % 9
            y = i//9
            try:

                value = int(grid[y, x])
                new2[i] = j + [value]
            except:
                break

    for i, j in enumerate(new2):
        if len(j) != 10 and i < 81:
            x, y, w, h, lable = j
            cv2.putText(output_image, str(lable), (x+10+con, y+35+con),
                        cv2.FONT_HERSHEY_COMPLEX_SMALL, 2, (0, 0, 255), 1)
    return output_image

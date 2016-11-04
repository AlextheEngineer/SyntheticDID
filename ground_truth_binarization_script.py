#This file turns all the images in the designated folder into black & white
import sys, os, random, glob
import numpy as np
import cv2

for img_file_name in glob.glob(os.path.join("data/ground_truths/", "*.png")):
    print("image: " + img_file_name)
    img = cv2.imread(img_file_name, 0)
    #img_array = np.array(img)
    #black_white_img_array = cv2.cvtColor(img_array, cv2.COLOR_BGR2GRAY)
    #black_white_img_array[black_white_img_array < 255] = 0
    #cv2.imwrite(img_file_name, black_white_img_array)
    th3 = cv2.adaptiveThreshold(img,255,cv2.ADAPTIVE_THRESH_GAUSSIAN_C,\
    cv2.THRESH_BINARY,35,5)
    cv2.imwrite(img_file_name, th3)
    
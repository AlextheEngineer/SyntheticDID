#This file turns all the images in the designated folder into black & white
import sys, os, random, glob
import numpy as np
import cv2

for img_file_name in glob.glob(os.path.join("data/ground_truths/", "*.png")):
	print("image: " + img_file_name)
	img = cv2.imread(img_file_name)
	img[img != 255] = 0
	cv2.imwrite(img_file_name, img)
	
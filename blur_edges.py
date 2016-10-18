
import os, glob
import sys
import cv2
import numpy as np
import numpy.random
import scipy.ndimage
import re

BLUR_SIZE = 0.75
ERODE_SIZE = 5

#in_file = sys.argv[1]
#out_file = sys.argv[2]
#out_dir = sys.argv[3] if len(sys.argv) >= 4 else None

#Read a file to load word images
word_image_location_file = open("paths/word_image_folder_paths.txt","r")
word_image_folder_list = word_image_location_file.readlines()
for idx, item in enumerate(word_image_folder_list):
	word_image_folder_list[idx] = item.rstrip('\r\n')
print("Word input folders")
print(word_image_folder_list)
dest_path = "data/blurred_words/"

for word_img_folder in word_image_folder_list:
    new_dirname = os.path.basename(os.path.normpath(word_img_folder))
    print(new_dirname)
    os.makedirs(dest_path+new_dirname, exist_ok=True)
    for img_file_name in glob.glob(os.path.join(word_img_folder, "*.png")):
        im = cv2.imread(img_file_name, 0)
        print(img_file_name.replace("\\","/"))
		#print (im.shape)
		#if out_dir:
		#	cv2.imwrite(os.path.join(out_dir, 'original_im.png'), im)
        original_mask = np.zeros_like(im)
        original_mask[im != 255] = 1
		#if out_dir:
		#	cv2.imwrite(os.path.join(out_dir, 'original_mask.png'), 255 * original_mask)

        blurred = scipy.ndimage.gaussian_filter(im, (BLUR_SIZE, BLUR_SIZE), truncate=2)
		#if out_dir:
		#	cv2.imwrite(os.path.join(out_dir, 'blurred_im.png'), blurred)

        eroded = scipy.ndimage.grey_erosion(im, size=(ERODE_SIZE,ERODE_SIZE))
		#if out_dir:
		#	cv2.imwrite(os.path.join(out_dir, 'eroded.png'), eroded)

        eroded_mask = np.zeros_like(eroded)
        eroded_mask[np.logical_and(eroded != 255, original_mask != 1)] = 2
		#if out_dir:
		#	cv2.imwrite(os.path.join(out_dir, "eroded_mask.png"), 255 * eroded_mask)

        out = im * original_mask + eroded_mask * blurred + (1 - (original_mask + eroded_mask)) * 255
		#if out_dir:
		#	cv2.imwrite(os.path.join(out_dir, "out.png"), out)
        img_name = os.path.basename(img_file_name)
        print("img_name: " + img_name)
        cv2.imwrite(dest_path + new_dirname + "/" + img_name, out)



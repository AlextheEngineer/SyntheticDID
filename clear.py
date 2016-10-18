#This file clears all the images in data/outputs, data/blank_bgs and data/ground_truths
import os

directory='data/outputs/'
os.chdir(directory)
filelist = [ f for f in os.listdir(".") if f.endswith(".png") ]
for f in filelist:
    os.remove(f)
  
directory='../../data/blank_bgs/'
os.chdir(directory)  
filelist = [ f for f in os.listdir(".") if f.endswith(".png") ]
for f in filelist:
    os.remove(f)
 
directory='../../data/ground_truths/'
os.chdir(directory)  
filelist = [ f for f in os.listdir(".") if f.endswith(".png") ]
for f in filelist:
    os.remove(f)
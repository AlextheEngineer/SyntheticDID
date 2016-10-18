#This file should put random stains on all the output images
import sys
import cv2

if len(sys.argv)!= 6:
	print("Incorrect parameters")
	print("Usage: \npython output_stainer.py input_path output_path strength density iterations")
	sys.exit()

path_to_input = sys.argv[1]
path_to_output = sys.argv[2]
strength = sys.argv[3]
density = sys.argv[4]
iterations = sys.argv[5]
#Read a file to load stains
stain_paths_file = open("paths/stain_folder_paths.txt","r")
stain_paths_list = stain_paths_file.readlines()
for idx, item in enumerate(stain_paths_list):
	stain_paths_list[idx] = item.rstrip('\r\n')

#Construct the script
from lxml import etree
root = etree.Element("root")
#Fill the background with words
alias_e = etree.SubElement(root, "alias")
alias_e.set("id", "INPUT")
#Example: 
    #<alias id="INPUT" value="test_backgrounds/bg1_resized.png"/>
alias_e.set("value", path_to_input)
#Example: 
    #<image id="my-image">
    #	<load file="INPUT"/>
    #</image>
image_e = etree.SubElement(root, "image")
image_e.set("id", "my-image")
load_e = etree.SubElement(image_e, "load")
load_e.set("file", "INPUT")
#Example:
    #<image id="my-copy">
    #	<copy ref="my-image"/>
    #</image>
image_e2 = etree.SubElement(root, "image")
image_e2.set("id", "my-copy")
copy_e2 = etree.SubElement(image_e2, "copy")
copy_e2.set("ref","my-image")
for stain_folder in stain_paths_list:
    #Example:
        #<gradient-degradations ref="my-copy">
        #<strength>1.2</strength>
        #<density>25</density>
        #<iterations>750</iterations>
        #<source>data/spots</source>
        #</gradient-degradations>	
    gradient_degradation_e = etree.SubElement(root, "gradient-degradations")
    gradient_degradation_e.set("ref", "my-copy")
    strength_e = etree.SubElement(gradient_degradation_e, "strength")
    strength_e.text = strength
    density_e = etree.SubElement(gradient_degradation_e, "density")
    density_e.text = density
    iterations_e = etree.SubElement(gradient_degradation_e, "iterations")
    iterations_e.text = iterations
    source_e = etree.SubElement(gradient_degradation_e, "source")
    source_e.text = stain_folder

#Example:
    #<save ref="my-copy" file="outputs/text_insertion_test1.png"/>
save_e = etree.SubElement(root, "save")
save_e.set("ref", "my-copy")
save_e.set("file", path_to_output)

output_xml = open("data_stainer_script.xml", 'w')
output_xml.write(etree.tostring(root, pretty_print=True).decode("utf-8"))

#Read input: 
#1.desired number of outputs
#2.Left Margin
#3.Top Margin
#4.Inter word spacing
#5.Inter line spacing
#6.Output path
import sys, os, random
import numpy as np
import cv2
# Member functions
def is_valid_location(x_value, y_value, word_spacing, line_spacing, 
left_margin, top_margin, word_image_path, bg_image_width, bg_image_height):
	word_img = cv2.imread(word_image_path)
	word_height, word_width, word_channels = word_img.shape
	if (x_value + word_width) > bg_image_width:
		if(y_value + line_spacing + word_height) > bg_image_height:
			return False, False, -1, -1
		else:
			return False, True, left_margin, y_value + word_height + line_spacing
	else:
		return True, True, x_value + word_width + word_spacing, y_value

if len(sys.argv)!=9:
	print("Incorrect parameters")
	print("Usage: \npython script_generator.py output_num left_margin top_margin word_spacing line_spacing \nstain_strength_scale stain_density_scale output_path")
	sys.exit()

output_num = int(sys.argv[1])
left_margin = int(sys.argv[2])
top_margin = int(sys.argv[3])
word_spacing = int(sys.argv[4])
line_spacing = int(sys.argv[5])
stain_strength_scale = sys.argv[6]
stain_density_scale = sys.argv[7]
output_path = sys.argv[8]
print("\n")
print("--Parameters:")
print("		output_num: "+str(output_num))
print("		left_margin: "+str(left_margin))
print("		top_margin: "+str(top_margin))
print("		word_spacing: "+str(word_spacing))
print("		line_spacing: "+str(line_spacing))
print("		output_path: "+output_path)
print("\n")

#Read a file to load word images
word_image_location_file = open("paths/blurred_word_image_folder_paths.txt","r")
word_image_folder_list = word_image_location_file.readlines()
for idx, item in enumerate(word_image_folder_list):
	word_image_folder_list[idx] = item.rstrip('\r\n')
print("Word input folders")
print(word_image_folder_list)

#Read a file to load background images
bg_image_location_file = open("paths/word_bg_folder_paths.txt","r")
bg_image_folder_list = bg_image_location_file.readlines()
for idx, item in enumerate(bg_image_folder_list):
	bg_image_folder_list[idx] = item.rstrip('\r\n')
print("Bg input folders")
print(bg_image_folder_list)

#Get [output_num] random background images, for each one of them, randomly paste input images

#Construct xml script
from lxml import etree
x_value = left_margin
y_value = top_margin
root = etree.Element("root")
#For each output
for i in range(output_num):
	#Fill the background with words
	alias_e = etree.SubElement(root, "alias")
	alias_e.set("id", "INPUT")
	#Example: <alias id="INPUT" value="test_backgrounds/bg1_resized.png"/>
	bg_rand_folder = random.choice(bg_image_folder_list)
	bg_image_name = random.choice(os.listdir(bg_rand_folder))
	alias_e.set("value", bg_rand_folder + bg_image_name)
	bg_img = cv2.imread(bg_rand_folder + bg_image_name)
	bg_image_height, bg_image_width, bg_channels = bg_img.shape
	#Create blank version of the bg
	blank_image = np.zeros((bg_image_height,bg_image_width,3), np.uint8)
	blank_image[::]=(255,255,255)
	cv2.imwrite("data/blank_bgs/"+bg_image_name, blank_image)
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
	#Example:
        #<manual-gradient-degradations ref="my-copy">
	manual_gradient_degradation_e = etree.SubElement(root, "manual-gradient-degradations")
	manual_gradient_degradation_e.set("ref", "my-copy")
	has_v_space = True
	has_h_space = True
	while(has_v_space == True):
        #Example:
            #<degradation>
            #<file>test_backgrounds/sample_text.png</file>
            #<strength>1</strength>
            #<x>0</x>
            #<y>0</y>
            #</degradation>
		word_rand_folder = random.choice(word_image_folder_list)
		word_image_name = random.choice(os.listdir(word_rand_folder))
		has_h_space, has_v_space, x_next_value, y_next_value = is_valid_location(x_value, y_value, word_spacing, line_spacing, 
		left_margin, top_margin, word_rand_folder + word_image_name, bg_image_width, bg_image_height)
		if has_v_space == False:
			x_value = left_margin
			y_value = top_margin
			break
		if has_h_space == False:
			x_value = x_next_value
			y_value = y_next_value
			continue
			
		degradation_e = etree.SubElement(manual_gradient_degradation_e, "degradation")
		file_e = etree.SubElement(degradation_e, "file")
		file_e.text = word_rand_folder + word_image_name
		strength_e = etree.SubElement(degradation_e, "strength")
		strength_e.text = "1"
		
		x_e = etree.SubElement(degradation_e, "x")
		x_e.text = str(x_value)
		y_e = etree.SubElement(degradation_e, "y")
		y_e.text = str(y_value)
		x_value = x_next_value
		y_value = y_next_value
    #Example:
        #...
        #<multi-core/>
        #<iterations>500</iterations>
        #</manual-gradient-degradations>
	multi_core_e = etree.SubElement(manual_gradient_degradation_e, "multi-core")
	iterations_e = etree.SubElement(manual_gradient_degradation_e, "iterations")
	iterations_e.text = "500"
	#Example:
        #<save ref="my-copy" file="outputs/text_insertion_test1.png"/>
	save_e = etree.SubElement(root, "save")
	save_e.set("ref", "my-copy")
	save_e.set("file", "data/outputs/degraded_"+bg_image_name)
	
output_xml = open("data_generator_script.xml", 'w')
output_xml.write(etree.tostring(root, pretty_print=True).decode("utf-8"))
#match_output_xml = open("match_generator_script.xml", 'w')
for element in root.findall("alias"):
	old_value = element.get("value")
	splited_value = old_value.split("/")
	splited_value[len(splited_value)-3] = "blank_bgs"
	del splited_value[len(splited_value)-2]
	element.set("value", "/".join(splited_value))
for element in root.findall("save"):
	old_value = element.get("file")
	splitted_value = old_value.split("/")
	splitted_value[len(splitted_value)-1] = splitted_value[len(splitted_value)-1]
	splitted_value[len(splitted_value)-2] = "ground_truths"
	element.set("file", "/".join(splitted_value))
white_bg_xml = open("match_generator_script.xml", 'w')
white_bg_xml.write(etree.tostring(root, pretty_print=True).decode("utf-8"))
	
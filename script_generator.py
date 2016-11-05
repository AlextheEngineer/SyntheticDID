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
def is_valid_location(x_value, y_value, word_spacing, line_spacing, max_row_height, 
left_margin, top_margin, word_image_path, bg_image_width, bg_image_height):
    word_img = cv2.imread(word_image_path)
    word_height, word_width, word_channels = word_img.shape
    if (x_value + word_width) > bg_image_width:
        if(y_value + line_spacing + word_height) > bg_image_height:
            return False, False, -1, -1, -1
        else:
            return False, True, left_margin, y_value + max_row_height + line_spacing, word_height
    else:
        if(y_value + line_spacing + word_height) > bg_image_height:
            return False, False, -1, -1, -1
        else:
            return True, True, x_value + word_width + word_spacing, y_value, word_height

if len(sys.argv)!=4:
    print("Incorrect parameters")
    print("Usage: python script_generator.py output_num stain_level(1-5) text_noisy_level(1-5)")
    #print("Usage: python script_generator.py output_num left_margin top_margin word_spacing line_spacing")
    #print("stain_strength_low_bound stain_strength_high_bound stain_density_low_bound stain_density_high_bound")
    #print("word_horizontal_shear_scale word_vertical_shear_scale word_rotation_scale word_color_jitter_sigma")
    #print("word_elastic_sigma word_blur_sigma_low_bound word_blur_sigma_high_bound word_margin")
    sys.exit()

output_num = int(sys.argv[1])
stain_level = float(sys.argv[2])
text_noisy_level = float(sys.argv[3])
#Parameter checking
if(output_num < 0):
    print("Invalid output_num, can't be negative")
    sys.exit()
if(stain_level < 1 or stain_level > 5):
    print("Invalid stain_level, has to be between 1 and 5")
    sys.exit()
if(text_noisy_level < 1 or text_noisy_level > 5):
    print("Invalid text_noisy_level, has to be between 1 and 5")
    sys.exit()

left_margin = 10#int(sys.argv[2])
top_margin = 10#int(sys.argv[3])
word_spacing = 10#int(sys.argv[4])
line_spacing = 10#int(sys.argv[5])
stain_strength_low_bound = 0.1*stain_level
stain_strength_high_bound = 0.1 + 0.1*stain_level
stain_density_low_bound = 2 + 0.1*stain_level
stain_density_high_bound = 2 + 0.1*stain_level
word_horizontal_shear_scale = 5 + 2*text_noisy_level
word_vertical_shear_scale = 5 + 2*text_noisy_level
word_rotation_scale = 5 + 2*text_noisy_level
word_color_jitter_sigma = 1 + 0.1*text_noisy_level
word_elastic_sigma = 5 - 0.2*text_noisy_level
word_blur_sigma_low_bound = 0.5 + 0.1*text_noisy_level
word_blur_sigma_high_bound = 1 + 0.1*text_noisy_level
word_margin = 5
#stain_strength_low_bound = float(sys.argv[6])
#stain_strength_high_bound = float(sys.argv[7])
#stain_density_low_bound = float(sys.argv[8])
#stain_density_high_bound = float(sys.argv[9])
#word_horizontal_shear_scale = float(sys.argv[10])
#word_vertical_shear_scale = float(sys.argv[11])
#word_rotation_scale = float(sys.argv[12])
#word_color_jitter_sigma = float(sys.argv[13])
#word_elastic_sigma = float(sys.argv[14])
#word_blur_sigma_low_bound = float(sys.argv[15])
#word_blur_sigma_high_bound = float(sys.argv[16])
#word_margin = int(sys.argv[17])

print("\n")
print("--Parameters:")
print("     output_num: "+str(output_num))
print("     left_margin: "+str(left_margin))
print("     top_margin: "+str(top_margin))
print("     word_spacing: "+str(word_spacing))
print("     line_spacing: "+str(line_spacing))
print("     stain_strength_range: ["+str(stain_strength_low_bound)+", "+str(stain_strength_high_bound)+"]")
print("     stain_density_range: ["+str(stain_density_low_bound)+", "+str(stain_density_high_bound)+"]")
print("     word_horizontal_shear_scale: "+str(word_horizontal_shear_scale))
print("     word_vertical_shear_scale: "+str(word_vertical_shear_scale))
print("     word_rotation_scale: "+str(word_rotation_scale))
print("     word_color_jitter_sigma: "+str(word_color_jitter_sigma))
print("     word_elastic_sigma: "+str(word_elastic_sigma))
print("     word_margin: "+str(word_margin))
print("     word_blur_sigma_range: ["+str(word_blur_sigma_low_bound)+", "+str(word_blur_sigma_high_bound)+"]")
print("\n")

#Macro
transformed_words_dest_path = "data/transformed_words/"

#Read a file to load word images
word_image_location_file = open("paths/word_image_folder_paths.txt","r")
word_image_folder_list = word_image_location_file.readlines()
for idx, item in enumerate(word_image_folder_list):
    word_image_folder_list[idx] = item.rstrip('\r\n')
#print("Word input folders")
#print(word_image_folder_list)

#Read a file to load background images
bg_image_location_file = open("paths/word_bg_folder_paths.txt","r")
bg_image_folder_list = bg_image_location_file.readlines()
for idx, item in enumerate(bg_image_folder_list):
    bg_image_folder_list[idx] = item.rstrip('\r\n')
#print("Bg input folders")
#print(bg_image_folder_list)

#Read a file to load stain paths
stain_paths_file = open("paths/stain_folder_paths.txt","r")
stain_paths_list = stain_paths_file.readlines()
for idx, item in enumerate(stain_paths_list):
    stain_paths_list[idx] = item.rstrip('\r\n')

#Get [output_num] random background images, for each one of them, randomly paste input images

#Construct xml script
from lxml import etree
x_value = left_margin
y_value = top_margin
root = etree.Element("root")

existing_output_num = len(os.listdir('data/outputs'))
#For each output
for i in range(output_num):
    output_index = existing_output_num + i
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
        #   <load file="INPUT"/>
        #</image>
    image_e = etree.SubElement(root, "image")
    image_e.set("id", "my-image")
    load_e = etree.SubElement(image_e, "load")
    load_e.set("file", "INPUT")
    #Example:
        #<image id="my-copy">
        #   <copy ref="my-image"/>
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
    max_row_height = 0
    word_count = 0
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
        #Perform random transformations, save in data/transfromed_words
        generated_image_name = str(output_index) + "_" + str(word_count) + "_" + word_image_name
        from word_transform import get_random_img_transform
        #Randomize transform parameters
        rand_h_shear_dg = random.random()*word_horizontal_shear_scale
        rand_v_shear_dg = random.random()*word_vertical_shear_scale
        rand_rotation_dg = random.random()*word_rotation_scale
        rand_color_jitter_sigma = random.random()*word_color_jitter_sigma
        rand_elastic_sigma = word_elastic_sigma + (random.random()-1)*0.1
        rand_blur_sigma = random.uniform(word_blur_sigma_low_bound, word_blur_sigma_high_bound)
        print("write path:"+transformed_words_dest_path+generated_image_name)
        rand_word_im = get_random_img_transform(word_rand_folder+word_image_name, \
        rand_h_shear_dg, rand_v_shear_dg, rand_rotation_dg, rand_color_jitter_sigma, \
        rand_elastic_sigma, rand_blur_sigma, word_margin)
        cv2.imwrite(transformed_words_dest_path+generated_image_name, rand_word_im)
        has_h_space, has_v_space, x_next_value, y_next_value, img_height = is_valid_location(x_value, y_value, word_spacing, line_spacing, max_row_height,\
        left_margin, top_margin, "data/transformed_words/" + generated_image_name, bg_image_width, bg_image_height)
        if(img_height > max_row_height):
            max_row_height = img_height
        if has_v_space == False:
            x_value = left_margin
            y_value = top_margin
            max_row_height = 0
            break
        if has_h_space == False:
            x_value = x_next_value
            y_value = y_next_value
            max_row_height = 0
            continue
            
        degradation_e = etree.SubElement(manual_gradient_degradation_e, "degradation")
        file_e = etree.SubElement(degradation_e, "file")
        file_e.text = transformed_words_dest_path+generated_image_name#word_rand_folder + word_image_name
        strength_e = etree.SubElement(degradation_e, "strength")
        strength_e.text = "1"
        
        x_e = etree.SubElement(degradation_e, "x")
        x_e.text = str(x_value)
        y_e = etree.SubElement(degradation_e, "y")
        y_e.text = str(y_value)
        x_value = x_next_value
        y_value = y_next_value
        
        word_count += 1
    #Example:
        #...
        #<multi-core/>
        #<iterations>500</iterations>
        #</manual-gradient-degradations>
    multi_core_e = etree.SubElement(manual_gradient_degradation_e, "multi-core")
    iterations_e = etree.SubElement(manual_gradient_degradation_e, "iterations")
    iterations_e.text = "500"
    #Add stains
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
        strength_e.text = "{:.2f}".format(random.uniform(stain_strength_low_bound, stain_strength_high_bound))
        density_e = etree.SubElement(gradient_degradation_e, "density")
        density_e.text = "{:.2f}".format(random.uniform(stain_density_low_bound, stain_density_high_bound))
        iterations_e = etree.SubElement(gradient_degradation_e, "iterations")
        iterations_e.text = "750"
        source_e = etree.SubElement(gradient_degradation_e, "source")
        source_e.text = stain_folder
    #Example:
        #<save ref="my-copy" file="outputs    ext_insertion_test1.png"/>
    save_e = etree.SubElement(root, "save")
    save_e.set("ref", "my-copy")
    save_e.set("file", "data/outputs/degraded_"+str(output_index)+"_"+bg_image_name)
    
output_xml = open("data_generator_script.xml", 'w')
output_xml.write(etree.tostring(root, pretty_print=True).decode("utf-8"))
#match_output_xml = open("match_generator_script.xml", 'w')
for element in root.xpath('//gradient-degradations' ) :
    element.getparent().remove(element)
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
    original_img_name = splitted_value[len(splitted_value)-1]
    element.set("file", "/".join(splitted_value))
white_bg_xml = open("match_generator_script.xml", 'w')
white_bg_xml.write(etree.tostring(root, pretty_print=True).decode("utf-8"))
print("match_generator_script.xml created")
print("data_generator_script.xml created")
print("Usage: java -jar Divadid.jar YOUR_XML.xml")
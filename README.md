# SyntheticDID
README

This documentation will cover how to correctly generate synthetic images for binarization

1. script_generator.py
    *This python file generates the XML file, which then gets run by
    using the following command:
        java -jar DivaDid.jar data_generator_script.xml
    
    *The python file takes in the following parameters:
        1. number of outputs
        2. left margin
        3. top margin
        4. word spacing
        5. line spacing
        6. output path
    
    *Generates the blank images(in data/blank_bgs/) with the sizes matching
    the randomly chosen background images, which will be used to generater 
    ground truths files(in data/ground_truths.)

    *Outputs another XML file named "match_generator_script.xml", which gets
    run by using the following command:
        java -jar DivaDid.jar match_generator_script.xml
    This command performs the same actions as the "data_generator_script.xml", 
    except it's on the corresponding blank backgrounds, right after this, you 
    should run:
        python ground_truth_binarization_script.py
    to finish generating the ground truth images.
    
    *To specify the paths for the folders containing your word images, edit paths
    in "paths/word_image_folder_paths.txt"(Also read documentation for blur_edges.py
    if you seek to blur the word images)
    
    *To specify the paths for the folders containing your background images, edit
    paths in "paths/word_bg_folder_paths.txt"
    
2. blur_edges.py
    *This python file will blur all the word images in the specified folders, run
    using the following command:
        python blur_edges.py 
     
    *Specify the folders of word images to blur by editing 
    "paths/blurred_word_image_folder_paths"
    
    *The output will be 
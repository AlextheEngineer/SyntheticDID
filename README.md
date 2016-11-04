# SyntheticDID

This documentation will cover how to correctly generate synthesized images for training neural-networks

Requirements:
    OpenCV, Python(currently using 3.5.2), Java(currently using 1.8.0_101)

References:
    https://diuf.unifr.ch/main/hisdoc/divadid-document-image-degradation

1. script_generator.py
    *The python file takes in the following parameters:
        1. number of outputs
        2. stain level(float:1-5)
        3. text noisiness level(float:1-5)
    
    *And performs the following actions:
    
        1.Generates the XML file, which then gets run by using the following command using
        DivaDid:
            java -jar DivaDid.jar data_generator_script.xml
        Running this script will generate synthesized degraded documents(in "data/outputs")
    
        2.Generates the blank images(in "data/blank_bgs/") with the sizes matching
        the randomly chosen background images, which will be used to generate 
        ground truths files(in "data/ground_truths")

        3. Generates another XML file named "match_generator_script.xml", which gets
        run by using the following command:
            java -jar DivaDid.jar match_generator_script.xml
        This command performs the same actions as the "data_generator_script.xml", 
        except it's on the corresponding blank backgrounds, right after this, you 
        should run:
            python ground_truth_binarization_script.py
        to finish generating the ground truth images which are in "data/ground_truths".
    
    *To specify the paths for the folders containing your word images, edit paths
    in "paths/word_image_folder_paths.txt", putting word folders in "data/input_words"
    is recommended.
    
    *To specify the paths for the folders containing your background images, edit
    paths in "paths/word_bg_folder_paths.txt", putting background folders in "data/input_bgs"
    is recommended.
    
    *To specify the paths for the folders containing your stain patches, edit paths in 
    "paths/stain_folder_paths.txt", putting stain image folders in "data/stains" is 
    recommended.
    
    *The python file also takes in the text noisiness level and apply a series of 
    transformations to each randomly chosen word. The transformed images are located
    at "data/transformed_words".
    
2. clear.py
    *For convenience, this file clears all the images in "data/blank_bgs/", 
    "data/ground_truths", "data/outputs" and "data/transformed_words". So user can 
    regenerate images without having to hand-delete the images before.
    
3. ground_truth_binarization_script.py
    *This python file converts the DivaDid version of the ground truth to black & white.
    Since the raw images created by command 
    "java -jar DivaDid.jar match_generator_script.xml"
    are not black & white. All the ground truth files are in "data/ground_truths"
import os
import subprocess
from argparse import ArgumentParser
from pathlib import Path

def get_options():
    parser = ArgumentParser(usage="helicon_focus.py -i sample_dir -o out_dir",
                            description="")
    parser.add_argument("-i", "--input", dest="sample_dir", type=Path,
                        help="The directory that contains all sorted images.")
    parser.add_argument("-o", "--output", dest="output_dir", type=Path, default=None,
                        help="Output directory. Make clustering at the original directory if not provided. ")
    parser.add_argument("--quiet", dest="quiet", default=False,
                        help="Quiet mode. ")
    return parser.parse_args()

def main():
    options = get_options()
    change_the_original = False
    
    # check the output_dir
    if options.output_dir is None:
        options.output_dir = options.sample_dir
        change_the_original = True
        if not options.quiet:
            sys.stdout.write("Warning: output not provided! Making changes to the original dir! \n")
    
    # get the directionary of sorted images
    sort_folder_dir = options.sample_dir
    output_folder_dir = options.output_dir

    # get the names of the rotation folder
    rotation_folder_name = sorted(os.listdir(sort_folder_dir))

    # get the directionary of the rotation folder
    # get the names and directionary of the angle folder
    for folder in rotation_folder_name:
        rotation_folder_path = os.path.join(str(sort_folder_dir)+"/"+folder)
        angle_folder_name = os.listdir(rotation_folder_path)
        for file in angle_folder_name:
            angle_file_path = os.path.join(str(rotation_folder_path)+"/"+file)
            output_file_name = os.path.join(str(output_folder_dir)+"/"+folder+"/"+"focused_"+file+".dng")
            subprocess.call(["/Applications/HeliconFocus.app/Contents/MacOS/HeliconFocus", "-silent", angle_file_path, "-save:"+output_file_name, "-mp:1", "-rp:8", "-sp:4"])

if __name__ == '__main__':
    main()


# the command line of helicon is 
# /Applications/HeliconFocus.app/Contents/MacOS/HeliconFocus -silent input_path -save:output_file_name -mp:1 -rp:8 -sp:4
# -save:output_file_name is very trikky, we need + to connect them when we use subprocess.call
import os
from re import sub
import commonTools
import customizedYaml
import csv
import cv2
from pathlib import Path
from generate_all_slides import decode_img_data, output_file
import multiprocessing
from functools import partial
from contextlib import contextmanager
from functools import reduce

'''
This script is aiming at create the record for all specimen images. Data to be included are:
1. core, sub_core and grid of the specimen image
2. genus species of the images
3. Resolution of the images, path of the images.
'''
@contextmanager
def poolcontext(*args, **kwargs):
    pool = multiprocessing.Pool(*args, **kwargs)
    yield pool
    pool.terminate()

def decode_img_data(all_img_data):
    core = all_img_data[0]
    # assuming the length is either 4 or 5
    if len(all_img_data)==4:
        sub_core = all_img_data[1]
    else:
        sub_core = all_img_data[1]+'_'+all_img_data[2]
    grid = int(all_img_data[-2])

    return core, sub_core, grid

def get_all_species_images(species, image_data_path, base_dir):
    genus = species.split(' ')[0]
    species_img_path  = os.path.join(image_data_path, species)
    specimen_out_data = []
    for specimen_imgs in os.listdir(species_img_path):
        specimen_metadata = specimen_imgs.split('_')
        core, sub_core, grid = decode_img_data(specimen_metadata)
        img_path = os.path.join(species_img_path, specimen_imgs)
        img = cv2.imread(img_path)
        height, width, _ = img.shape
        img_path_out = img_path.replace(base_dir,'')
        specimen_out_data.append([core, sub_core, grid, height, width, genus, species, img_path_out])
    return specimen_out_data



def image_data_handler(img_data_path, base_dir):
    all_species = [folder for folder in commonTools.folders(img_data_path)]
    processes = multiprocessing.cpu_count() - 2
    with poolcontext(processes=processes) as pool:
        all_data = pool.map(partial(get_all_species_images, image_data_path = img_data_path, base_dir = base_dir), all_species)
    pool.close()
    agg_data = reduce((lambda x,y: x+y), all_data)
    output_file(agg_data, 'specimen_data.csv')

if __name__ == '__main__':
    params = commonTools.parse_opt()
    yaml_data = customizedYaml.yaml_handler(params.yaml)
    base_dir = yaml_data.data['base_path']
    img_data_path = os.path.join(base_dir, 'class_images')
    image_data_handler(img_data_path,base_dir)
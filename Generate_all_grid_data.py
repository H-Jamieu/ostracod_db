from ast import main
import os
import commonTools
import customizedYaml
import csv
import cv2
import pandas as pd
from pathlib import Path
from generate_all_slides import decode_img_data, output_file
import multiprocessing
from functools import partial
from contextlib import contextmanager
from functools import reduce
import xml.etree.ElementTree as ET
import regex as re
'''
This script is aming at creating the annotation data for all annotation files. Using the pascalVOC annotation as reference file, the data included in the script should be:
    1. Core, sub_core, grid -> created by re-use the grid functions
    2. Type of annotation: raw, species, genus, raw-yolo, species-yolo, genus-yolo
    3. annotation path
    4. Read into the annotation, find the count of the ostracods.
'''

@contextmanager
def poolcontext(*args, **kwargs):
    pool = multiprocessing.Pool(*args, **kwargs)
    yield pool
    pool.terminate()

def determine_annotation_type(annotation_root):
    if bool(re.search('pseudo',annotation_root.lower())):
        return 'pseudo'
    elif bool(re.search('genus',annotation_root.lower())):
        return 'genus'
    elif bool(re.search('species', annotation_root.lower())):
        return 'species'


def get_ostracod_count(xml_annotation):
    objects = xml_annotation.findall('object')
    return len(objects)


def get_annotation_data(annotation_slides, annotation_root, base_dir):
    slide_data = annotation_slides.split('_')
    core, sub_core, _ = decode_img_data(slide_data)
    annotation_type = determine_annotation_type(annotation_root)
    annotation_parent_dir = os.path.join(annotation_root, annotation_slides)
    annotation_data = []
    for annotations in os.listdir(annotation_parent_dir):
        grid_name = Path(annotations).stem
        grid_num = int(grid_name.split('_')[-1])
        annotation_dir = os.path.join(annotation_parent_dir, annotations)
        xml_annotation = ET.parse(annotation_dir)
        ostracod_cnt = get_ostracod_count(xml_annotation)
        out_annotation_dir = annotation_dir.replace(base_dir,'')
        annotation_data.append([core, sub_core, grid_num, annotation_type, ostracod_cnt, out_annotation_dir])
    return annotation_data



def annotation_handler(annotation_path, base_dir):
    all_annotations = [folder for folder in commonTools.folders(annotation_path)]
    print(all_annotations[0])
    # list dir to find all slides with the specified annotation.
    processes = 1 #multiprocessing.cpu_count() - 31
    with poolcontext(processes=processes) as pool:
        all_data = pool.map(partial(get_annotation_data, annotation_root = annotation_path, base_dir = base_dir), all_annotations)
    pool.close()
    agg_data = reduce((lambda x,y: x+y), all_data)
    annotation_type = determine_annotation_type(annotation_path)
    out_name = 'grid_annotation_'+annotation_type+'.csv'
    output_file(agg_data, out_name)



if __name__=='__main__':
    params = commonTools.parse_opt()
    yaml_data = customizedYaml.yaml_handler(params.yaml)
    base_dir = yaml_data.data['base_path']
    yaml_data.build_default_paths()
    pseudo_annotation = yaml_data.data['pseudo_pascal_voc']
    genus_annotation = yaml_data.data['genus_pascal_voc']
    species_annotation = yaml_data.data['species_pascal_voc']
    # Yolo annotation stay hold on since it is not complete
    annotation_handler(pseudo_annotation, base_dir)
    annotation_handler(genus_annotation, base_dir)
    annotation_handler(species_annotation, base_dir)

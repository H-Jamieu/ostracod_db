from email.mime import base
import os
import commonTools
import customizedYaml
import csv
import cv2
from pathlib import Path

'''
load the image shots and get its path. Getting slide, core, sub-core and the magnification form the file name
'''

def decode_img_data(img_data):
    '''
    img_data: a list contains the splitted image data. Sample: ['HKUV12','FD','63','50X']
    '''
    core = img_data[0]
    len_data = len(img_data)
    if len_data == 1:
        # PPP case
        mgn = '50X'
    else:
        mgn = img_data[-1]
    if len_data <= 2:
        # FD403 case
        sub_core = ''
    else:
        sub_core='_'.join(img_data[1:-1])
    return core, sub_core, mgn

def output_file(slide_data, file_name='slide_data_raw.csv'):
    with open(file_name, 'w', newline="") as fout:
        csv_writer = csv.writer(fout)
        csv_writer.writerows(slide_data)

def scan_all_raw(raw_dir,base_dir):
    all_data = []
    for images in os.listdir(raw_dir):
        # I can build a database for the images' resolution
        image_path = os.path.join(raw_dir, images)
        img = cv2.imread(image_path)
        height, width, _ = img.shape
        img_name = Path(image_path).stem
        img_data = img_name.split('_')
        core, sub_core, mgn = decode_img_data(img_data)
        rel_path = image_path.replace(base_dir,'')
        all_data.append([core,sub_core,mgn,height,width,rel_path])
    output_file(all_data)
    
if __name__ == '__main__':
    params = commonTools.parse_opt()
    yaml_data = customizedYaml.yaml_handler(params.yaml)
    base_dir = yaml_data.data['base_path']
    raw_dir = os.path.join(base_dir,'raw_images')
    scan_all_raw(raw_dir, base_dir)
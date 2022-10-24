import os
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

@contextmanager
def poolcontext(*args, **kwargs):
    pool = multiprocessing.Pool(*args, **kwargs)
    yield pool
    pool.terminate()

def get_grid_data(slides, grid_base_dir, base_dir):
    '''
    Get core, slide, magnification from slides. Get grid number, width, height from the grid images
    '''
    img_data = slides.split('_')
    core, sub_core, mgn = decode_img_data(img_data)
    grid_path = os.path.join(grid_base_dir,slides)
    data_pend = []
    for grids in os.listdir(grid_path):
        # Some annotation files were mixed into the fodler
        if grids.endswith('.tif'):
            grid_name = Path(grids).stem
            grid_num = int(grid_name.split('_')[-1])
            image_folder = os.path.join(grid_base_dir, slides)
            image_path = os.path.join(image_folder, grids)
            img = cv2.imread(image_path)
            height, width, _ = img.shape
            grid_image_path = image_path.replace(base_dir,'')
            data_pend.append([core, sub_core, grid_num, mgn, height, width, grid_image_path])
    return data_pend


def grid_data_handler(grid_base_dir, base_dir):
    '''
    Parallel this function across grids.
    '''
    all_slides = [folder for folder in commonTools.folders(grid_base_dir)]
    processes = multiprocessing.cpu_count() - 8
    with poolcontext(processes=processes) as pool:
        all_data = pool.map(partial(get_grid_data, grid_base_dir = grid_base_dir, base_dir = base_dir), all_slides)
    pool.close()
    agg_data = reduce((lambda x,y: x+y), all_data)
    output_file(agg_data, 'grid_data_base.csv')
        
                

if __name__ == '__main__':
    params = commonTools.parse_opt()
    yaml_data = customizedYaml.yaml_handler(params.yaml)
    base_dir = yaml_data.data['base_path']
    grid_base_dir = os.path.join(base_dir,'Grid_images')
    grid_data_handler(grid_base_dir, base_dir)
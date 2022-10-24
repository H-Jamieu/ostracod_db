import os
import pandas as pd

'''
This script is doing the id generation work of the database. Output of the script is the table ready for insertion 
'''
# Constant for building ID.
ID_LENGTH = 15

def ID_build(ID_keyword, ID_sequence):
    FILL_LENGTH = ID_LENGTH - len(ID_keyword)
    ID = ID_keyword+str(ID_sequence).zfill(FILL_LENGTH)
    return ID

def slide_data_module(slide_data):
    ID_keyword = 'SLIDE'

if __name__ == '__main__':
    grid_data = pd.read_csv('grid_data_base.csv')
    slide_data = pd.read_csv('slide_data.csv')
    specimen_data = pd.read_csv('specimen_data.csv')
    annotation_genus = pd.read_csv('grid_annotation_genus.csv')
    annotation_pseudo = pd.read_csv('grid_annotation_pseudo.csv')
    annotation_species = pd.read_csv('grid_annotation_species.csv')
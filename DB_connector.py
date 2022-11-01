import os
import mysql.connector
from mysql.connector import errorcode
import customizedYaml
import commonTools
import pandas as pd
from pathlib import PurePath, Path
import shutil
import itertools

'''
Connecting the DB with python data handling module, this is a draft script that included all actions.
Opeartions I want to do:
    1. Get the error record using the record file.
    2. Change the record's status code to the corresponding error type in the original record file.
    3. Export the error files in 'Export' folder for reference.
This is an experimental script to investigate the python mysql connector.
'''

config = {
    'user': 'root',
    'password': '12345678',
    'host': '127.0.0.1',
    'database': 'ostracods_data'
}

def copy_to_dest(error_path, base_path, export_path):
    export_error_path = export_path+error_path#os.path.join(export_path, error_path)
    if Path(export_error_path).suffix == '.tif':
        export_error_path = export_error_path.replace("Grid_images", "pseudo_annotation\\pascal_voc")
    p = PurePath(export_error_path).parents[0]
    Path(p).mkdir(parents=True, exist_ok=True)
    source_path = base_path+error_path#os.path.join(base_path, error_path)
    shutil.copy(source_path, export_error_path)

def retrive_existing_error(cnx, base_path, export_path):
    '''
    get the updated result from the DB.
    '''
    get_query = ("select grid_path, annotation_path "
                 "from grid_data, grid_annotations "
                 "where status_code = 2 "
                 "and grid_data.grid_id = grid_annotations.grid_id "
                 "and annotation_type = 'pseudo';")
    cur = cnx.cursor()
    cur.execute(get_query)
    all_errors = cur.fetchall()
    all_outputs = list(set(itertools.chain(*all_errors)))
    for o in all_outputs:
        copy_to_dest(o, base_path, export_path)
    cur.close()

def getting_match(df, v):
    return df.loc[(df['core']==v[0]) & (df['slide']==v[1]) & (df['grid']==v[2])]

def loc_unaffected(df, search_list):
    all_df= []
    for val in search_list:
        all_df.append(getting_match(df, val))
    effect_df = pd.concat(all_df)
    return effect_df


def update_error_records(cnx, record):
    """
    Method: First update the status code in the db, then get all results with corresponding status code
    """
    cur = cnx.cursor()
    update_status = ("update grid_data, slide_id_hub "
                     "set grid_data.status_code = 2 "
                     "where grid_data.slide_id = slide_id_hub.slide_id "
                     "and slide_id_hub.core = %(core)s "
                     "and slide_id_hub.sub_core = %(sub_core)s "
                     "and grid_data.grid_no = %(grid_no)s;")
    un_updated = []
    total_affected = 0
    effect_cols = ['core', 'slide', 'grid']
    effect_search = record[effect_cols].value_counts()
    for val, cnt in effect_search.iteritems():
        update_data = {
            "core": val[0],
            "sub_core": val[1],
            "grid_no": val[2]
        }
        cur.execute(update_status, update_data)
        affected_rows = cur.rowcount
        if affected_rows == 0:
            un_updated.append(val)
        else:
            # how many rows in the error record affected
            total_affected += cnt
    not_in_db = loc_unaffected(record, un_updated)
    print(f'{total_affected} rows affected!')
    cnx.commit()
    #retrive_existing_error(cur)
    cur.close()
    return not_in_db

if __name__ == '__main__':
    try:
        cnx = mysql.connector.connect(user=config['user'],
                                      database=config['database'],
                                      password=config['password'],
                                      host=config['host'])
    except mysql.connector.Error as err:
        if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
            print("Something is wrong with your user name or password")
        elif err.errno == errorcode.ER_BAD_DB_ERROR:
            print("Database does not exist")
        else:
            print(err)
    else:
        params = commonTools.parse_opt()
        yaml_data = customizedYaml.yaml_handler(params.yaml)
        export_path = yaml_data.data['export_path']
        base_path = yaml_data.data['base_path']
        error_data_path = os.path.join(base_path, 'error_record.csv')
        # error_data = pd.read_csv(error_data_path)
        # not_in_db = update_error_records(cnx, error_data)
        # not_in_db.to_csv('not_in_db.csv',index=None)
        retrive_existing_error(cnx, base_path, export_path)
        cnx.close()

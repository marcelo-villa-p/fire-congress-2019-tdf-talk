#!/usr/bin/env python3
# =============================================================================
# Date:     February, 2019
# Author:   Marcelo Villa P.
# Purpose:  Downloads data files from a previously created task using the
#           AppEEARS API.
# Notes:    If the task is not done the program will repeatedly sleep until the
#           task is done. The program skips all non-data files such as quality
#           files, metadata and readme like files.
# =============================================================================
import cgi
import json
import os
import re

import requests


def download_task(task_id, user, pwd, layers, save_to, seconds=300):
    """
    Downloads all the files from a specified AppEEARS task.

    :param task_id: task id
    :param user:    Earthdata username
    :param pwd:     Earthdata password
    :param layers:  list of products and their respective layers
    :param save_to: path to save the products to
    :return:        None
    """
    api = 'https://lpdaacsvc.cr.usgs.gov/appeears/api'
    basenames = ['_'.join([item['product'], item['layer']]) for item in layers]

    # get token and build header
    token = requests.post(f'{api}/login', auth=(user, pwd)).json()['token']
    header = {'Authorization': f'Bearer {token}'}

    # check if task is done
    status = requests.get(f'{api}/status/{task_id}', headers=header).json()
    if status['status'] != 'done':
        raise Exception(f'Task {task_id} is not done yet.')

    # call the bundle API to get the files' information
    bundle = requests.get(f'{api}/bundle/{task_id}').json()
    fids = [f['file_id'] for f in bundle['files']]

    for fid in fids:
        # call the bundle API with a specific file id
        dl = requests.get(f'{api}/bundle/{task_id}/{fid}', stream=True)

        # get filename and destination folder, discarding medatafiles
        cd = dl.headers['Content-Disposition']
        fn = os.path.basename(cgi.parse_header(cd)[1]['filename'])

        # check if file is a data file
        if fn.startswith(tuple(basenames)):
            # get product's (without version) name of the file
            product = re.compile('([^.|-]+)').match(fn).group()
            product_path = os.path.join(save_to, product)

            # create folder if it does not exist
            if not os.path.exists(product_path):
                os.makedirs(product_path)

            # download file (if it has not been downloaded yet)
            path = os.path.join(save_to, 'original', product, fn)
            if not os.path.exists(path):
                with open(path, 'wb') as f:
                    for data in dl.iter_content(chunk_size=8192):
                        f.write(data)
                print(f'{path} downloaded.')
            else:
                print(f'{path} already exists.')


if __name__ == '__main__':
    # get Earthdata username and password
    user = os.environ.get('EARTHDATA_USER')
    pwd = os.environ.get('EARTHDATA_PASS')

    # define path to save the products to
    save_to = '../../data/tif/MODIS'

    tasks_info_filenames = os.listdir('../../data/json/appeears_tasks')
    for task_info_fn in tasks_info_filenames:
        # read task info and download data
        with open(f'../../data/json/appeears_tasks/{task_info_fn}') as f:
            info = json.load(f)
            task_id = info['task_id']
            layers = info['layers']
        download_task(task_id, user, pwd, layers, save_to)

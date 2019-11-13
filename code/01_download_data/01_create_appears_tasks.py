#!/usr/bin/env python3
# =============================================================================
# Date:     February, 2019
# Author:   Marcelo Villa P.
# Purpose:  Creates a task using the AppEEARS API to retrieve four MODIS
#           products and their respective layers:
#               - MOD14A2.006  (Thermal Anomalies & Fire)
#               - MCD12Q1.006  (Land Cover Type)
#               - MOD44B.006   (Vegetation Continuous Fields)
#               - MOD13A3.006  (EVI)
# Notes:    In order to create a request using the AppEEARS API you need to
#           have an Earthdata account. If you need to register, go to:
#           https://urs.earthdata.nasa.gov/users/new
#           For more information about the AppEEARS API go to:
#           https://lpdaacsvc.cr.usgs.gov/appeears/api/
# =============================================================================
import datetime
import json
import os

import requests


def create_task(task_type, task_name, dates, layers, geo, of, proj, user, pwd):
    """
    Creates a task using the AppEEARS API.
    :param task_type:   task type
    :param task_name:   task name
    :param dates:       start and end of the date range for which to extract
                        data
    :param layers:      product and version identifier for the product and the
                        name of the layer
    :param geo:         GeoJSON object defining the spatial region of interest
    :param of:          output file type
    :param proj:        projection name
    :param user:        Earth data username
    :param pwd:         Earthdata password
    :return:            task id
    """
    api = 'https://lpdaacsvc.cr.usgs.gov/appeears/api'  # api url

    # create task template
    task = {
        'task_type': task_type,
        'task_name': task_name,
        'params': {
            'dates': dates,
            'layers': layers,
            'geo': geo,
            'output': {
                'format': {'type': of},
                'projection': proj
            },
        }
    }

    # get token and build header
    token = requests.post(f'{api}/login', auth=(user, pwd)).json()['token']
    header = {'Authorization': f'Bearer {token}'}

    # post a call to the API task service
    r = requests.post(f'{api}/task', json=task, headers=header)

    # check if call was successful
    if r.status_code == 202:
        return r.json()['task_id']
    else:
        raise Exception(f'Error creating task: {r.json()["message"]}')


if __name__ == '__main__':
    # define products and layers to request
    layers = [{'layer': 'FireMask', 'product': 'MOD14A2.006'},
              {'layer': 'LC_Type2', 'product': 'MCD12Q1.006'},
              {'layer': 'Percent_Tree_Cover', 'product': 'MOD44B.006'},
              {'layer': '_1_km_monthly_EVI', 'product': 'MOD13A3.006'}]

    # define dates for each layer
    dates = [{'startDate': '01-01-2002', 'endDate': '12-31-2016'},
             {'startDate': '01-01-2002', 'endDate': '12-31-2016'},
             {'startDate': '01-01-2001', 'endDate': '12-31-2016'},
             {'startDate': '01-10-2001', 'endDate': '12-31-2016'}]

    # set other task parameters
    task_type = 'area'
    of = 'geotiff'
    proj = 'geographic'
    with open('../../data/json/geo/COL.json') as f:
        geo = json.load(f)
        del geo['crs']  # delete the crs from the JSON

    # get Earthdata username and password
    user = os.environ.get('EARTHDATA_USER')
    pwd = os.environ.get('EARTHDATA_PASS')

    # create a directory to store individual tasks information
    tasks_info_path = '../../data/json/appeears_tasks'
    if not os.path.exists(tasks_info_path):
        os.makedirs(tasks_info_path)

    for lyr, dt in zip(layers, dates):
        date = datetime.datetime.today().strftime("%Y-%m-%d")
        task_name = f'MODIS_{lyr["product"]}_{date}'

        # create task and store task information as JSON
        task_id = create_task(task_type, task_name, [dt], [lyr], geo, of, proj,
                              user, pwd)

        # write task information
        task_fn = f'task_{task_id}.json'
        with open(f'{tasks_info_path}/{task_fn}', 'w') as f:
            info = {
                'date': str(datetime.datetime.today()),
                'task_id': task_id,
                'task_name': task_name,
                'layers': [lyr]
            }
            json.dump(info, f)

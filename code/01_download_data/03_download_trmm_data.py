#!/usr/bin/env python3
# =============================================================================
# Date:     November, 2019
# Author:   Marcelo Villa P.
# Purpose:  Downloads one of the Tropical Rainfall Measuring Mission (TRMM)
#           products (3B43) monthly files from NASA's Precipitation Processing
#           System (PPS).
# Notes:    This script takes a text file provided by PPS as input. The text
#           file consists in a list of URLs pointing to the requests files. To
#           submit a request go to:
#           https://storm.pps.eosdis.nasa.gov/storm/data/Service.jsp?serviceName=Order
#           and make sure to check the FTP URL box at the Script Type section
#           before submitting the request.
# =============================================================================
import os
import shutil
import urllib.request as request
from contextlib import closing


def download_file(url, save_to):
    """
    Downloads a file from an URL to a specified folder. Lightly adapted from:
    https://stackoverflow.com/a/11768443/7144368.
    :param url:     file's URL
    :param save_to: folder to save the file to
    :return:        path to the saved file
    """
    fn = os.path.basename(url)
    path = os.path.join(save_to, fn)
    with closing(request.urlopen(url)) as r:
        with open(path, 'wb') as f:
            shutil.copyfileobj(r, f)


if __name__ == '__main__':
    # define folder to save the files to
    save_to = '../../data/hdf/TRMM/3B43/original'
    if not os.path.exists(save_to):
        os.makedirs(save_to)

    # open STORM's generated .txt file and download every file
    with open('../../data/txt/ftp_url_005_201911120612.txt', 'r') as txt:
        for url in txt:
            download_file(url.strip(), save_to)

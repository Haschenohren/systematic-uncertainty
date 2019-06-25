#!/usr/bin/python3
#Run this file to download the data from the phenix website.
#Requires requests and lxml packages.
#pip install requests lxml

import requests, os
from lxml import html
from urllib.parse import urljoin

def scrape(url, dir):
    '''Scrape files from table at url and place them in given directory'''
    #read html file for scraping
    response = requests.get(url, verify=False)
    doc = html.fromstring(response.content)
    #scrape the list of urls from every link in the table
    file_list = doc.xpath('//tr[position()>1]/td[1]/a/@href')
    download_files(url, dir, file_list)


def download_files(base_url, out_dir, filenames):
    '''Downloads the list of files to given output directory'''
    os.makedirs(out_dir, exist_ok=True)
    print('Downloaded 0 files.', end='')
    count = 0
    for filename in filenames:
        url = urljoin(base_url, filename)
        out_path = urljoin(out_dir, filename)
        response = requests.get(url, verify=False)
        f = open(out_path, 'w')
        f.write(response.text)
        f.close()
        count += 1
        print(f'\rDownloaded {count} files.', end='')
    print()


if __name__=='__main__':
    print('This scraper will throw many SSL errors. To surpress these errors,',
        'use "-W ignore" option in python command.')
    base = 'https://www.phenix.bnl.gov/phenix/WWW/info/data/ppg146/'
    folders = ['Figure4/', 'Figure11/', 'Figure12/']
    for folder in folders:
        scrape(base + folder, 'data/' + folder)
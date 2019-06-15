#!/usr/bin/python3
#requires requests and lxml libraries

#this will throw a lot of insecure request warnings because certifi
#doesn't seem to like phenix's certificate authority

#to supress warnings use python -W ignore uncertainty.py

import requests, os, re
from lxml import html
from urllib.parse import urljoin

url = 'https://www.phenix.bnl.gov/phenix/WWW/info/data/ppg146/Figure4/'

#https://arxiv.org/abs/1304.3410 table 4
_uncertainty_table = (
	(.09, .09, .11, .11, .10, .10),
	(.10, .10, .11, .11, .11, .11),
	(.14, .14, '-', '-', .14, .14),
	(.08, .08, .13, .13, .09, .09),
	(.09, .09, .13, .13, .11, .11)
)
#dictionary for determining column of table based on particle type/charge
_col_select = {'pospion': 0, 'negpion': 1, 'poskaon': 2, 'negkaon':3, 'posprot': 4, 'negprot': 5}
def systematic_uncertainty(particle, collision, p_T, value_yield):
	#select a table entry based on particle type/charge, collision, and transverse momentum
	if collision == 'AuAu':
		row = 0 if p_T < 3 else 1 if p_T <= 5 else 2
	else:
		row = 3 if p_T < 3 else 4
	col = _col_select[particle]
	return _uncertainty_table[row][col] * value_yield
	

def scrape_filenames(url):
	#read the html file for scraping
	response = requests.get(url, verify=False)
	file_table = html.fromstring(response.content)
	return file_table.xpath('//tr[position()>1]/td[1]/a/@href')
	

def download_files(base_url, filenames):
	'''Downloads the list of files to data/ directory'''
	if not os.path.exists('data/'):
		os.mkdir('data/')
	print('Downloaded 0 files.', end='')
	count = 0
	for filename in filenames:
		url = urljoin(base_url, filename)
		response = requests.get(url, verify=False)
		f = open('data/' + filename, 'w')
		f.write(response.text)
		f.close()
		count += 1
		print(f'\rDownloaded {count} files.', end='')
	print()
	
	
def append_su(filenames):
	if not os.path.exists('data_org/'):
		os.mkdir('data_org/')
	for filename in filenames:
		#get the particle and collision types from the filename
		particle, collision = filename.split('_')[:2]
		#open file and append systematic uncertainty column
		filepath = 'data/' + filename
		with open(filepath, 'r') as f:
			original = f.read()
		with open(filepath, 'w') as f:
			for row in original.splitlines():
				cols = row.split()
				p_T = float(cols[0])
				value_yield = float(cols[1])
				su = systematic_uncertainty(particle, collision, p_T, value_yield)
				f.write(f'{row}\t{su}\n')
	print('Appended systematic uncertainty column to all files.')

def reorganize(filenames):
	#split filenamess into their 'groups' and centralities
	pattern = re.compile(r'(\D+)_(cent\d+)\D+')
	grouped_files = {}
	for filename in filenames:
		#extract the group name and the centrality from the filename
		m = pattern.match(filename)
		group, centrality = m.group(1,2)
		if not group in grouped_files:
			grouped_files[group] = open(f'data_org/{group}.txt', 'w')
		#concatenate file to the correct grouped file
		with open(f'data/{filename}', 'r') as infile:
			outfile = grouped_files[group]
			outfile.write(f'{centrality}\n')
			outfile.write(infile.read())
			outfile.write('\n')
	for f in grouped_files.values():
		f.close()
	print(f'Concatenated {len(filenames)} files into {len(grouped_files)}.')


if __name__ == '__main__':
	files = scrape_filenames(url)
	download_files(url, files)
	append_su(files)
	reorganize(files)
	
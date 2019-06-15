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
def systematic_uncertainty(particle, collision, p_T, inv_yield):
	#select a table entry based on particle type/charge, collision, and transverse momentum
	if collision == 'AuAu':
		row = 0 if p_T < 3 else 1 if p_T <= 5 else 2
	else:
		row = 3 if p_T < 3 else 4
	col = _col_select[particle]
	return _uncertainty_table[row][col] * inv_yield


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
				inv_yield = float(cols[1])
				su = systematic_uncertainty(particle, collision, p_T, inv_yield)
				#format with 6 significant figures
				f.write(f'{row}\t{su:.6g}\n')
	print('Appended systematic uncertainty column to all files.')


def reorganize(filenames):
	if not os.path.exists('data_org/'):
		os.mkdir('data_org/')
	#split filenamess into their 'groups' and centralities
	pattern = re.compile(r'(\D+)_cent(\d+)\D+')
	#construct dictionary of lists of files that should be grouped together
	file_groups = {}
	for filename in filenames:
		#extract the group name and the centrality from the filename
		m = pattern.match(filename)
		group, centrality = m.group(1,2)
		if not group in file_groups:
			file_groups[group] = [(filename, centrality)]
		else:
			file_groups[group].append((filename, centrality))
	for group, group_files in file_groups.items():
		write_concatenated_file(group + '.txt', group_files)
	print(f'Organized {len(filenames)} files into {len(file_groups)}.')


def write_concatenated_file(outfile_name, file_centrality_pairs):
	#Use sort key to sort tuples by filename, and place 0-100% range first in order
	sort_key = lambda pair: pair[0].replace('0100', '0000')
	file_centrality_pairs.sort(key=sort_key)
	outfile = open('data_org/' + outfile_name, 'w')
	for filename, centrality in file_centrality_pairs:
		infile = open('data/' + filename, 'r')
		#construct header for table
		min_cent = int(centrality[:2])
		max_cent = int(centrality[-2:])
		#special case: file ends with 0100 (0-100%)
		if centrality == '0100':
			min_cent, max_cent = 0, 100
		outfile.write(f'Centrality {min_cent}-{max_cent}%\n')
		#construct and print table
		table = construct_table(infile.read())
		outfile.write(table + '\n')
		infile.close()
	outfile.close()


def construct_table(data_str):
	#Extract data into 2d list
	table = [row.split('\t') for row in data_str.splitlines()]
	#Append table header row to table
	table.insert(0, ['pT', 'Inv. Yield', 'Stat. Err.', 'Sys. Err'])
	num_cols = len(table[0])
	col_widths = [0] * num_cols
	#Determine column widths by maximum widths of each field in each column
	for row in table:
		for c, field in enumerate(row):
			col_widths[c] = max(col_widths[c], len(field))
	#Add formatted fields to table str
	for row in table:
		for c, field in enumerate(row):
			w = col_widths[c]
			#overwrite field with padded field
			row[c] = f'{field:{w}}'
	table_str = '\n'.join('  '.join(row) for row in table) + '\n'
	return table_str


if __name__ == '__main__':
	files = scrape_filenames(url)
	download_files(url, files)
	append_su(files)
	reorganize(files)
	
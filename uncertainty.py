#!/usr/bin/python3
#requires requests and lxml libraries

#this will throw a lot of insecure request warnings because certifi
#doesn't seem to like phenix's certificate authority

#to supress warnings use python -W ignore uncertainty.py


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
	

#retrieve and modify the files

import requests
from lxml import html
from urllib.parse import urljoin

#read the figure 4 html file for scraping
url = 'https://www.phenix.bnl.gov/phenix/WWW/info/data/ppg146/Figure4/'
response = requests.get(url, verify=False)
file_table = html.fromstring(response.content)

finished_count = 0
#open each txt file url, add systematic uncertainty, and save to disk
for filename in file_table.xpath('//tr[position()>1]/td[1]/a/@href'):
	txt_url = urljoin(url, filename)
	txt_response = requests.get(txt_url, verify=False)
	
	#get the particle and collision types from the filename
	particle, collision = filename.split('_')[:2]
	
	#write downloaded data to file, appending systematic uncertainty
	with open(filename, 'w') as f:
		#read retrieved file line by line
		for line in txt_response.text.splitlines():
			cols = line.split()
			p_T = float(cols[0])
			value_yield = float(cols[1])
			su = systematic_uncertainty(particle, collision, p_T, value_yield)
			#write original 3-column data and appended uncertainty
			f.write(f'{line}\t{su}\n')
			
	finished_count += 1
	print(f'\rfiles finished: {finished_count}', end='')
	
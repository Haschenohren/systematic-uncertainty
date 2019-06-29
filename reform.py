#!/usr/bin/python3
#Reform the data files into collections of datasets with good formatting and
#with systematic uncertainty columns
from uncertainty import systematic_uncertainty
from dataset import dataset
import re, os


def gather_dir_structure():
    '''searches every directory in the data/ folder for files
       and stores those files in a dictionary'''
    dir_list = []
    with os.scandir('data/') as entries:
        for entry in entries:
            if entry.is_dir():
                dir_list.append(entry.name)
    dir_structure = {dir: [] for dir in dir_list}
    for dir in dir_list:
        with os.scandir(f'data/{dir}') as entries:
            for entry in entries:
                if entry.is_file():
                    dir_structure[dir].append(entry.name)
        print(f'Found {len(dir_structure[dir])} files in data/{dir}')
    return dir_structure


def reshape_dir_structure(dir_structure):
    '''restructure directory structure so that the files are grouped in
       groups based on their collision system, charge, particle species'''
    reshaped = {}
    for dir, files in dir_structure.items():
        if not dir in reshaped.keys():
            reshaped[dir] = {}
        for f in files:
            #group is the filename without the cent####.txt at the end
            #To group different centralities of the same collision system
            #and particle together
            group = f[:-len('_cent####.txt')]
            if not group in reshaped[dir].keys():
                reshaped[dir][group] = [f]
            elif 'cent0100' in f:
                #Make sure 0-100 centrality is in the right order
                reshaped[dir][group].insert(0,f)
            else:
                reshaped[dir][group].append(f)
    return reshaped


def create_reformed_files(dir_structure):
    '''Create new files for each group of files given by dir_structure'''
    for dir, group in dir_structure.items():
        out_path = 'data_org/' + dir
        os.makedirs(out_path, exist_ok=True)
        count = 0
        for group_name, file_list in group.items():
            out_file = open(f'{out_path}/{group_name}.txt', 'w')
            for filename in file_list:
                metadata = parse_filename(filename)
                col_headers = ['pT', metadata['value_type'], 'Stat. Err']
                in_file = open(f'data/{dir}/{filename}', 'r')
                d = dataset(in_file.read(), col_headers)
                in_file.close()
                col_func = create_column_function(metadata)
                d.create_column('Sys. Err', col_func)
                out_file.write(f'Centrality {metadata["cent_low"]}-'
                    f'{metadata["cent_high"]}%\n')
                out_file.write(f'{d}\n\n')
            out_file.close()
            count += 1
        print(f'{count} files created in {out_path}')


#big bad regex: determines species, charge, collision system, centrality, 
#value (inv. yield or nmf)
re_nmf_cs = r'(?P<nmf_cs>raa|rda)' #nuclear modification factor in collision sys
re_charge = r'(?P<charge>neg|pos)'
re_species = r'(?P<species>kaon|pion|prot)'
re_col_sys = r'(?P<col_sys>AuAu|dAu)' #collision system
re_cent = r'cent(?P<cent>\d{4})' #centrality
regex = f'{re_nmf_cs}?_?{re_charge}?{re_species}_{re_col_sys}?_?{re_cent}.txt'
pattern = re.compile(regex)

def parse_filename(filename):
    '''uses regex to obtain metadata from file name in the form
       (collision_system, species, charge, value_type, cent_low, cent_high)
       where value type is RAA, RdA, or Inv. Yield'''
    match = pattern.match(filename)
    if match == None:
        raise ValueError('filename does not match pattern')
    nmf_cs, col_sys = match.group('nmf_cs', 'col_sys')
    if nmf_cs == 'raa':
        value_type = 'RAA'
        col_sys = 'AuAu'
    elif nmf_cs == 'rda':
        value_type = 'RdA'
        col_sys = 'dAu'
    else:
        value_type = 'Inv. Yield'
    charge = match.group('charge')
    if charge != 'neg':
        charge = 'pos'
    species, cent = match.group('species', 'cent')
    if cent == '0100':
        cent_low, cent_high = '0', '100'
    else:
        cent_low, cent_high = cent[:2], cent[-2:]
    #package appropriate local variables into metadata dictionary
    metadata_dict = {k:v for k,v in locals().items() if k in
        {'col_sys', 'species', 'charge', 'value_type', 'cent_low', 'cent_high'}}
    return metadata_dict


def create_column_function(md):
    '''returns a function which is passed to the dataset.create_column method
       as the column creation function. Uses metadata from the
       parse_filename function'''
    def col_func(p_T, value, *_):
        su = systematic_uncertainty(
            md['col_sys'],
            md['species'], 
            md['charge'], 
            float(p_T), 
            float(value))
        return f'{su:.6g}'
    return col_func


if __name__ == '__main__':
    dirs = gather_dir_structure()
    dirs = reshape_dir_structure(dirs)
    print('Grouping files into collections of pretty tables...')
    create_reformed_files(dirs)
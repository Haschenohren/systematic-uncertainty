# systematic-uncertainty
Calculates systematic uncertainty for the data in https://www.phenix.bnl.gov/phenix/WWW/info/data/ppg146/Figure4/

Saves the modified data files to `data/` directory

Creates nice readable tables in the `data_org/` directory

`python -W ignore scrape.py` downloads the data files from the server

`python reform.py` collects the data together with each centrality in the same file, and also formats data as tables

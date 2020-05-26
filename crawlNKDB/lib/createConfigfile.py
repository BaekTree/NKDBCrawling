from configparser import ConfigParser

config = ConfigParser()

config['DB'] = {
    'MONGO_URI' : 'mongodb://localhost:27017',
    'MONGO_DB' : 'NKDB_with_all'
}

config['VARS'] = {
    'VAR1' : 'post_title',
    'VAR2' : 'post_body',
    'VAR3' : 'post_writer',
    'VAR4' : 'post_date',
    'VAR5' : 'published_institution',
    'VAR6' : 'published_institution_url',
    'VAR7' : 'top_category',
    'VAR8' : 'published_date',
    'VAR9' : 'file_name',
    'VAR10' : 'file_download_url',
    'VAR11' : 'file_id_in_fsfiles',
    'VAR12' : 'file_extracted_content'
}

import os
import sys
from pathlib import Path

split_unit = None
if os.name == "nt":
    split_unit = "\\"
else:
    split_unit = "/"

this_file_dir = os.path.abspath(__file__)
# print(this_file_dir)
dir_temp = this_file_dir.split(split_unit)
# print(dir_temp)
dir_temp.remove(dir_temp[-1])#createConfigFile.py
dir_temp[-1] = "spiders"#replace lib with spider
# print(dir_temp)
spider_dir = split_unit.join(dir_temp)
# print(spider_dir)


config['LOCAL'] = {
    'PATH_SPIDER' : spider_dir
}

config['SERVER'] = {
    'PATH_SPIDER' : spider_dir#'/home/hyeyoung/NKDBCrawling_capston/crawlNKDB/spiders'
}

with open('./config.cnf', 'w') as f:
    config.write(f)

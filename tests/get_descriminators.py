from abstract_utilities import *
from abstract_webtools import *
from abstract_solcatcher import *
from bs4 import BeautifulSoup
import re
import json

from bs4 import BeautifulSoup
import re

def get_parsed_log(idx,parsed_logs):
    parsed_logs_ = parsed_logs.copy()
    idx_ints = idx.split('.')
    for i,idx_int in enumerate(idx_ints):
        if i != 0:
            parsed_logs_ = parsed_logs_.get('children')
        idx_curr = int(idx_int)-1
        parsed_logs_ = parsed_logs_[idx_curr]
    return parsed_logs_
def make_dir(name,directory=None):
    directory = directory or get_caller_dir()
    nudir = os.path.join(directory,name)
    os.makedirs(nudir,exist_ok=True)
    return nudir
events_dir = make_dir('events')
dirs,files = get_files_and_dirs(events_dir,allowed_exts=['.html'])
for file_path in files:
    sig_dir = os.path.dirname(file_path)
    siganture = os.path.basename(sig_dir)
    print(siganture)
    event_dir = os.path.dirname(sig_dir)
    event = os.path.basename(event_dir)
    instructions_path = os.path.join(sig_dir,'instructions.json')
    instructions = safe_load_from_json(instructions_path)
    logdata = fetch_any_combo(columnNames='*', tableName='logdata', searchColumn='signature',searchValue=siganture)
    input(logdata)
    parsed_logs = logdata[0].get('parsed_logs')
    for instruction in instructions:
        idx = instruction.get('index')
        print(get_parsed_log(idx,parsed_logs))
        input(instruction)
##    soup_mgr = soupManager(source_code=contents)
##    text = soup_mgr.find_all('etails')
##    input(text)
##    #'Instruction Details'.join(contents.split('Instruction Details')[1:])
##    if 'Tree Show' in text:
##        texts = text.split('({')
##        event_name = texts[0].split(' ')[-1]
##        for part in text.split('({'):
##            part_spl = part.split('})')
##            part_spl[0]
##        input()

from abstract_utilities import *
dirs , files = get_files_and_dirs(get_caller_dir(),allowed_exts=['.json'])
for file in files:
    data = safe_read_from_json(file)
    input(data)

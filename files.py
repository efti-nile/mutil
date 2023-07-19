import os
import re
import shutil


def create_empty_folder(folder_path):
    if os.path.exists(folder_path):
        shutil.rmtree(folder_path)
    os.makedirs(folder_path)


def get_only_filename(file_path):
    base_name = os.path.basename(file_path)  
    filename, extension = os.path.splitext(base_name)  
    return filename


def add_postfix_to_name(file_path, prefix):
    result = re.sub(r'(\.[a-zA-Z0-9]+)$',
                    prefix + r'\1',
                    file_path)
    return result

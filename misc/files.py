import os
import re
import shutil
from pathlib import Path


def read_file(file_path: str, **kwargs) -> str:
    with open(file_path, 'r', **kwargs) as file:
        content = file.read()
    return content


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


def clean_names(input):
    """
    В указанной папке оставляет в именах файлов только начальные циферки.
    Пример: '1341 - копия.jpg' -> '1341.jpg'
    """
    input = Path(input)
    for item in input.iterdir():
        if item.is_file():
            name = item.name
            new_name = re.sub(r'(\d+).*\.', r'\1.', name)
            new_path = item.with_name(new_name)
            item.rename(new_path)

            
def add_prefix(input, prefix):
    "В указанной папке добавляет префикс к именам файлов"
    input = Path(input)
    for item in input.iterdir():
        if item.is_file():
            filename = item.name
            new_filename = prefix + filename
            new_filepath = item.with_name(new_filename)
            item.rename(new_filepath)

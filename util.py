import json
import os
import csv


def save_dictionary_to_json_file(file_name: str, data):

    with open(get_local_data_path(file_name), 'w') as fp:
        json.dump(data, fp, indent=4, sort_keys=True)



def load_dictionary_from_json_file(filename: str):
    with open(get_local_data_path(filename)) as file:
        ret = json.load(file)
        return ret


def append_row_to_file(lst: list, filename: str):
    with open(get_local_data_path(filename), mode='a', encoding='utf-8', newline='') as file:
        csv_writer = csv.writer(file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL, )

        csv_writer.writerow(lst)
    file.close()

def check_and_create_local_data_dir():
    if not os.path.exists(local_data_dir):
        os.makedirs(local_data_dir)

def get_local_data_path(filename: str):
    check_and_create_local_data_dir()
    return os.path.join(local_data_dir, filename)


local_data_dir = 'local_data'

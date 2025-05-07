import json


def load_json_file(file_path):
    with open(file_path, "r") as file:
        return json.load(file)


def load_txt_file(file_path):
    with open(file_path, "r") as file:
        return file.read()

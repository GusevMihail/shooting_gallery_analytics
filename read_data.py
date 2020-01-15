import json, io
import pandas as pd


def is_numeric_field(field_name: str):
    int_factor_names = ('cash', 'toys', 'mood', 'power_reserve', 'plan',
                        'exchange', 'collection', 'prepayment,', 'balance', 'are_you_good', 'good_day')
    for template in int_factor_names:
        if template in field_name:
            return True
    return False


def is_categorical_field(field_name: str):
    cat_factor_names = ('bolls', 'sticks', 'sockets', 'pellet', 'candis', 'envelope', 'reports')
    return field_name in cat_factor_names


def categorical_to_num(field: str):
    empty_field_value = -1
    convert_dict = {
        'нет': 0,
        'срочно': 1,
        'мало': 2,
        'хватает': 3,
        'много': 4}

    if field == '':
        return empty_field_value
    for pattern in convert_dict.keys():
        if pattern in field.lower():
            return convert_dict[pattern]


def process_fields(line):
    for field in line:
        line[field] = line[field][0]
        if is_numeric_field(field):
            if line[field] == '':
                line[field] = 0
            else:
                line[field] = int(line[field])
        else:
            if is_categorical_field(field):
                line[field] = categorical_to_num(line[field])


def process_line(line):
    if line['morning'] == {} or line['evening'] == {}:
        return 'Not morning or evening values'
    if not isinstance(line['morning']['date_time_str'], str):
        if len(line['morning']['date_time_str']) != 1 or len(line['evening']['date_time_str']) != 1:
            return "Values is't correct"
        process_fields(line['morning'])
        process_fields(line['evening'])


filename = "data_file.json"
with open(filename, encoding='utf-8') as data_file:
    data = json.load(data_file)
    # print(data)

for line in data:
    process_line(line)

df = pd.read_json(filename, encoding='utf-8')

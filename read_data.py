import json
import pandas as pd
from collections import defaultdict


def is_numeric_field(field_name: str):
    int_factor_names = ('cash', 'toys', 'mood', 'power_reserve', 'plan',
                        'exchange', 'collection', 'prepayment', 'balance', 'are_you_good', 'good_day')
    for template in int_factor_names:
        if template in field_name:
            return True
    return False


def is_categorical_field(field_name: str):
    cat_factor_names = ('bolls', 'sticks', 'sockets', 'pellet', 'candis', 'envelope', 'reports')
    return field_name in cat_factor_names


def is_list_field(field_name: str):
    list_factor_names = ('ok_guns', 'bed_guns')
    return field_name in list_factor_names


def str_to_num(field: str):
    if field == '' or field is None:
        return 0
    else:
        return int(float(field))


def categorical_to_num(field: str):
    empty_field_value = -1
    convert_dict = {
        'нет': 0,
        'срочно': 1,
        'мало': 2,
        'хватает': 3,
        'много': 4}

    if field == '' or field is None:
        return empty_field_value
    for pattern in convert_dict.keys():
        if pattern in field.lower():
            return convert_dict[pattern]


def process_fields(line):
    for field in line:
        if is_list_field(field):
            continue
        else:
            line[field] = line[field][0]  # explode single-element lists
        if is_numeric_field(field):
            line[field] = str_to_num(line[field])
            continue
        if is_categorical_field(field):
            line[field] = categorical_to_num(line[field])


def process_line(line):
    if line['morning'] == {}:
        return 'Not morning or evening values', line['evening']['user'][0]
    if line['evening'] == {}:
        return 'Not morning or evening values', line['morning']['user'][0]
    if not isinstance(line['morning']['date_time_str'], str):
        if len(line['morning']['date_time_str']) != 1:
            return "Values is't correct", line['morning']['user']
        if len(line['evening']['date_time_str']) != 1:
            return "Values is't correct", line['evening']['user']
    process_fields(line['morning'])
    process_fields(line['evening'])
    return None, line['morning']['user']


class UserDict:
    def __init__(self):
        self.name_dict = {}
        self.id_dict = {}

    def name_to_id(self, user_name: str):
        if user_name in self.name_dict:
            return self.name_dict[user_name]
        else:
            new_id = len(self.name_dict)
            self.name_dict[user_name] = new_id
            self.id_dict[new_id] = user_name
            return new_id

    def id_to_name(self, user_id: int):
        return self.id_dict[user_id]


def sorted_dict(d: dict):
    s = sorted(d.items(), key=lambda x: x[1], reverse=True)
    return s


filename = "data_file.json"
# filename = "test_file.json"
with open(filename, encoding='utf-8') as data_file:
    raw_data = json.load(data_file)
    # print(data)

data = []
users = UserDict()
er_no_one_r, er_duplicated_r = 0, 0
no_one_repord_users = defaultdict(int)
dublicated_repord_users = defaultdict(int)
for i, line in enumerate(raw_data):
    error, responsible_user = process_line(line)
    if error:
        # print(f'line{i}: {error}')  # print all errors
        if 'morning' in error:
            er_no_one_r += 1
            no_one_repord_users[responsible_user] += 1
        if "is't correct" in error:
            er_duplicated_r += 1
            for u in responsible_user:
                dublicated_repord_users[u] += 1
    else:
        data.append(line)

if __name__ == '__main__':
    print(f'no morning or evening lines: {er_no_one_r}')
    print(sorted_dict(no_one_repord_users))
    print(f'incorrect value lines: {er_duplicated_r}')
    print(sorted_dict(dublicated_repord_users))


def test_user_dict_class():
    ids = []
    for line in data[:10]:
        user_name = line['morning']['user']
        user_id = users.name_to_id(user_name)
        ids.append(user_id)
        print(f"{user_name:20} -> {user_id}")

    for user_id in ids:
        user_name = users.id_to_name(user_id)
        print(f"{user_id:3} -> {user_name}")


# UserDict test
# test_user_dict_class()

# df = pd.read_json(filename, encoding='utf-8')
df = pd.DataFrame(data)

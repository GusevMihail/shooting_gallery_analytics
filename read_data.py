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


def read_data_from_json(filename):
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
    return data


def read_data_from_csv(f_morning, f_evening):
    morning = pd.read_csv(f_morning, parse_dates=[0],
                          usecols=['Отметка времени', 'Тир', 'Оператор', 'Количество маленьких игрушек.',
                                   'Количество средних игрушек.', 'Количество больших игрушек.', 'Как настроение?'])
    names = dict(zip(morning.columns.values,
                     ['date', 'store', 'user', 'small_toys', 'medium_toys', 'big_toys', 'mood']))
    morning.rename(columns=names, inplace=True)

    evening = pd.read_csv(f_evening, parse_dates=[0],
                          usecols=['Отметка времени', 'Тир', 'Наличные.', 'Безнал'])
    names = dict(zip(evening.columns.values,
                     ['date', 'store', 'e_cash', 'e_cashless']))
    evening.rename(columns=names, inplace=True)

    return morning


def csv_data_cleanup(df):
    df = df.dropna()  # выкидываем строки, содержащие пропуски в данных

    # Приводим имена опреаторов в единому формату
    df.user = df.user.str.strip().str.title()

    # добавляем дополнительные столбцы с необходимыми данными
    df['income'] = df['e_cash'] + df['e_cashless']
    # df['date'] = pd.to_datetime(df.year * 10000 + df.month * 100 + df.day, format='%Y%m%d')
    df['day'] = df['date'].day
    df['month'] = df['date'].month
    df['year'] = df['date'].year
    # from datetime import datetime
    df['week_day'] = df['date'].apply(lambda x: x.weekday())

    # конвертируем нужные колонки в категории
    df.store = pd.Categorical(df.store)
    df.user = pd.Categorical(df.user)

    df = df.set_index(['date'])

    columns_to_research = ('income', 'day', 'month', 'year', 'week_day', 'store', 'user',
                           'small_toys', 'medium_toys', 'big_toys', 'mood',)

    # оставляем только нужные колонки
    df = df.reindex(columns=columns_to_research)

    # добавляем дополнительные признаки
    df['toys_volume'] = df['small_toys'] + df['medium_toys'] * 2 + df['big_toys'] * 5

    return df


# if __name__ == '__main__':
# print(f'no morning or evening lines: {er_no_one_r}')
# print(sorted_dict(no_one_repord_users))
# print(f'incorrect value lines: {er_duplicated_r}')
# print(sorted_dict(dublicated_repord_users))


# def test_user_dict_class():
#     ids = []
#     for line in data[:10]:
#         user_name = line['morning']['user']
#         user_id = users.name_to_id(user_name)
#         ids.append(user_id)
#         print(f"{user_name:20} -> {user_id}")
#
#     for user_id in ids:
#         user_name = users.id_to_name(user_id)
#         print(f"{user_id:3} -> {user_name}")


def json_data_cleanup(df):
    # убираем сложные поля утреннего и вечернего отчета, переименовываем вложенные поля,
    # добиваемся плоской структуры данных
    dfm = df['morning'].apply(pd.Series)
    dfe = df['evening'].apply(pd.Series)
    # оставляем поля из утреннего отчёта без префиксов, чтобы сократить названия полей конечного датасета
    # dfm.columns = 'm_' + dfm.columns 
    dfe.columns = 'e_' + dfe.columns
    df = pd.concat([df.drop(['morning', 'evening'], axis=1), dfm, dfe], axis=1)

    df = df.dropna()  # выкидываем строки, содержащие пропуски в данных

    # Приводим имена опреаторов в единому формату
    df.user = df.user.str.strip().str.title()

    # добавляем дополнительные столбцы с необходимыми данными
    df['income'] = df['e_cash'] + df['e_cashless']
    df['date'] = pd.to_datetime(df.year * 10000 + df.month * 100 + df.day, format='%Y%m%d')
    # from datetime import datetime
    df['week_day'] = df['date'].apply(lambda x: x.weekday())

    # конвертируем нужные колонки в категории
    df.store = pd.Categorical(df.store)
    df.user = pd.Categorical(df.user)

    df = df.set_index(['date'])

    columns_to_research = ('income', 'day', 'month', 'year', 'week_day', 'store', 'user',
                           'small_toys', 'medium_toys', 'big_toys', 'bolls', 'pellet', 'candis',
                           'mood', 'power_reserve', 'plan')

    # оставляем только нужные колонки
    df = df.reindex(columns=columns_to_research)

    # добавляем дополнительные признаки
    df['toys_volume'] = df['small_toys'] + df['medium_toys'] * 2 + df['big_toys'] * 5

    return df


def filter_rare_values(df, column: str, min_sample_count=10):
    sample_count = df.groupby([column]).income.count()
    df = df.reset_index().set_index([column])
    df = df.drop(sample_count[sample_count < min_sample_count].index)
    df = df.reset_index().set_index('date')
    df[column].cat.remove_unused_categories(inplace=True)

    return df


def build_users_rating(df):
    # by_store_normalization = (df.groupby(['store', 'user'])['income'].median() /
    #                           df.groupby(['store']).income.median()) \
    #     .reset_index().groupby(['user']).income.median()
    #
    # by_week_day_normalization = (df.groupby(['week_day', 'user'])['income'].median() /
    #                             df.groupby(['week_day']).income.median()) \
    #     .reset_index().groupby(['user']).income.median()

    by_store_week_day_normalization = (df.groupby(['week_day', 'store', 'user']).income.median() /
                                       df.groupby(['week_day', 'store']).income.median()) \
        .reset_index().groupby(['user']).income.median()

    by_month_normalization = (df.groupby(['month', 'user'])['income'].median() /
                              df.groupby(['month']).income.median()) \
        .reset_index().groupby(['user']).income.median()

    users_rating = pd.DataFrame()
    # users_rating['rating'] = (by_store_normalization + by_week_day_normalization + by_month_normalization) / 3
    users_rating['rating'] = by_store_week_day_normalization * by_month_normalization
    users_rating.sort_values(by='rating', ascending=False, inplace=True)

    # users_rating = (df.groupby(['store', 'user'])['income'].mean() /
    #                 df.groupby(['store']).income.mean())
    #
    # users_rating = users_rating.reset_index().groupby(['user']).mean().sort_values(by='income', ascending=False)
    # users_rating.columns = ['rating']
    return users_rating


source = 'json'  # 'json' or 'csv'

# читаем данные и проводим первичную очистку
if source == 'json':
    data = read_data_from_json('data_file.json')
    df = pd.DataFrame(data)
    df = json_data_cleanup(df)
elif source == 'csv':
    df = read_data_from_csv(r'.\data\morning.csv', r'.\data\evening.csv')
    df = csv_data_cleanup(df)
else:
    df = None
    raise Exception(f'invalid data source: {source}. Must be "json" or "csv"')

# бэкапим датасет со всеми данными;
# основной очищаем от работников и тиров, про которых слишком мало информации
df_with_rares = df.copy()
df = filter_rare_values(df, 'user', min_sample_count=10)
df = filter_rare_values(df, 'store', min_sample_count=30)
# строим таблицу рейтинга эффективности работников
users_rating = build_users_rating(df)

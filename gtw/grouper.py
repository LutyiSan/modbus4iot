from operator import itemgetter
from env import MULTI_READ
from csv_validator import Validator

PREFIX = "devices/"


def csv_to_dict(csv_file, csv_delimiter):
    with open(f"{PREFIX}{csv_file}", 'r') as fl:
        csv_txt = fl.read().splitlines()
    cols = csv_txt[0].split(csv_delimiter)
    result_dict = dict.fromkeys(cols)
    for col in cols:
        result_dict[col] = []
    idx = 0
    rows = len(csv_txt) - 1
    while idx < rows:
        idx += 1
        row = csv_txt[idx].split(csv_delimiter)
        c = -1
        for col in cols:
            c += 1
            if row[c] == '':
                row[c] = 'None'
            elif row[c].isdigit():
                row[c] = int(row[c])
            result_dict[col].append(row[c])
    validator = Validator()
    if validator.check_csv_data(result_dict):
        return result_dict
    else:
        return False


def get_signal_list(device):
    param_list = []
    count = len(device['reg_address']) - 1
    idx = -1
    while idx < count:
        idx += 1
        param = (
            device['name'][idx], device['reg_type'][idx], device['reg_address'][idx], device['quantity'][idx],
            device['bit_number'][idx],
            device['value_type'][idx], device['scale'][idx])
        param_list.append(param)
    # print(ldt)
    return param_list


def get_sorted_signal_dict(signals_list):
    signals = {"reg_type": [], 'reg_address': [], 'quantity': [], 'bit_number': [], 'value_type': [], 'scale': [],
               'name': []}
    sorted_list = sorted(signals_list, key=itemgetter(1, 2, 4))
    for value in sorted_list:
        signals['name'].append(value[0])
        signals['reg_type'].append(value[1])
        signals['reg_address'].append(value[2])
        signals['quantity'].append(value[3])
        signals['bit_number'].append(value[4])
        signals['value_type'].append(value[5])
        signals['scale'].append(value[6])
    return signals


class Grouper:
    def __init__(self, device):
        self.return_dict = {'start_address': [], 'read_quantity': [], 'reg_type': [], 'reg_address': [],
                            'quantity': [], 'value_type': [], 'bit_number': [], 'name': [], 'present_value': [],
                            'scale': []}
        self.signals = csv_to_dict(device, ';')
        if self.signals:
            self.signals = get_sorted_signal_dict(get_signal_list(self.signals))
            self.signals['start_address'] = []
            self.signals['read_quantity'] = []
            self.signals['present_value'] = []

    def grouping(self):
        if self.signals:
            if MULTI_READ > 125:
                max_query = 125
            else:
                max_query = MULTI_READ
            self.len_signals = len(self.signals['reg_address']) - 2
            self.start_address = self.signals['reg_address'][0]
            self.read_quantity = self.signals['quantity'][0]
            i = -1
            while i < self.len_signals:
                if self.read_quantity == max_query:
                    self.__append_group(self.start_address, self.read_quantity)
                    self.start_address = self.signals['reg_address'][i + 1]
                    self.read_quantity = 0
                i += 1
                if self.signals['reg_type'][i] == self.signals['reg_type'][i + 1]:
                    self.__type_grouper(i)
                else:
                    self.__append_group(self.start_address, self.read_quantity)
                    self.__type_grouper(i)
            self.__append_group(self.start_address, self.read_quantity)
            print(self.signals['start_address'], self.signals['read_quantity'])
            return self.signals
        else:
            return False

    def __append_group(self, *args):
        self.signals['start_address'].append(args[0])
        self.signals['read_quantity'].append(args[1])

    def __type_grouper(self, i):
        if self.signals['reg_address'][i] + self.signals['quantity'][i] == self.signals['reg_address'][i + 1]:
            self.read_quantity += self.signals['quantity'][i + 1]
        elif (self.signals['reg_address'][i] + self.signals['quantity'][i] != self.signals['reg_address'][
            i + 1]) \
                and self.signals['reg_address'][i] != self.signals['reg_address'][i + 1]:
            if self.read_quantity == 0:
                self.read_quantity = self.signals['quantity'][i]
            self.__append_group(self.start_address, self.read_quantity)
            self.start_address = self.signals['reg_address'][i + 1]
            self.read_quantity = self.signals['quantity'][i + 1]

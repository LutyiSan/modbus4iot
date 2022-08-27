import pandas as pd
from loguru import logger
from operator import itemgetter
from env import DEVICE_LIST

PREFIX = "gtw/devices/"


def get_device_dict(file):
    try:
        device_dict = pd.read_csv(f"{PREFIX}{file}", delimiter=";", index_col=False).to_dict('list')
        #  print(device_dict)
        return device_dict
    except Exception as e:
        logger.exception(f"FAIL read csv{file}", e)
        return False


def get_signal_list(device):
    ldt = []
    count = len(device['reg_address']) - 1
    idx = -1
    while idx < count:
        idx += 1

        dt = (
            device['name'][idx], device['reg_type'][idx], device['reg_address'][idx], device['quantity'][idx],
            device['bit_number'][idx],
            device['value_type'][idx], device['scale'][idx])
        ldt.append(dt)
    # print(ldt)
    return ldt


def get_sorted_signal_dict(signals_list):
    signals = {"reg_type": [], 'reg_address': [], 'quantity': [], 'bit_number': [], 'value_type': [], 'scale': [], 'name': []}
    sl = sorted(signals_list, key=itemgetter(1, 2, 4))
    for i in sl:
        signals['reg_type'].append(i[1])
        signals['reg_address'].append(i[2])
        signals['quantity'].append(i[3])
        signals['bit_number'].append(i[4])
        signals['value_type'].append(i[5])
        signals['scale'].append(i[6])
        signals['name'].append(i[0])
    # print(signals)
    return signals


class Grouper:
    def __init__(self):
        self.return_dict = {'start_address': [], 'read_quantity': [], 'reg_type': [], 'reg_address': [],
                            'quantity': [], 'value_type': [], 'bit_number': [], 'name': [], 'present_value': [],
                            'scale': []}
        self.signals = get_sorted_signal_dict(get_signal_list(get_device_dict(DEVICE_LIST[0])))
        print(self.signals['reg_address'])
        self.len_signals = len(self.signals['reg_address']) - 1
        self.reg_address = self.signals['reg_address']
        self.query_quantity = self.signals['quantity']
        self.reg_type = self.signals['reg_type']
        self.value_type = self.signals['value_type']
        self.bit_number = self.signals['bit_number']
        self.id = self.signals['name']
        self.return_dict['scale'] = self.signals['scale']
        self.start_register = self.reg_address[0]
        self.read_quantity = None

    # print(self.reg_type)

    def append_data(self, *args):
        self.return_dict['reg_address'].append(args[0])
        self.return_dict['quantity'].append(args[1])
        self.return_dict['value_type'].append(args[2])
        if args[3] is not None:
            self.return_dict['bit_number'].append(args[3])
        else:
            self.return_dict['bit_number'].append('none')
        self.return_dict['name'].append(args[4])
        print(f"First append address: {args[0]}  quantity: {args[1]}  value_type: {args[2]}")

    def append_second_data(self, *args):
        self.return_dict['start_address'].append(args[0])
        self.return_dict['read_quantity'].append(args[1])
        self.return_dict['reg_type'].append(args[2])
        print(f"Second append start_address: {args[0]}  read_quantity: {args[1]}  reg_type: {args[2]}")
    def grouping(self):
        max_quanty = 124
        self.read_quantity = self.query_quantity[0]
        idx = -1
        while idx < self.len_signals:
            idx += 1
            if idx != self.len_signals:
                # Если адрес регистра + длина запроса равны по значению следующему адресу и тип регистра одинаковый
                if (self.reg_address[idx] + self.query_quantity[idx] == self.reg_address[idx + 1]) and \
                        (self.reg_type[idx] == self.reg_type[idx + 1]):
                    print('if-1')
                    self.read_quantity += self.query_quantity[idx + 1]
                    self.append_data(self.reg_address[idx], self.query_quantity[idx],
                                     self.value_type[idx], self.bit_number[idx], self.id[idx])

                # Если адрес регистра такой же как и у следующего и у них одинаковый тип регистра
                elif (self.reg_address[idx] == self.reg_address[idx + 1]) and \
                        (self.reg_type[idx] == self.reg_type[idx + 1]):
                    print('elif-1')
                    self.append_data(self.reg_address[idx], self.query_quantity[idx],
                                     self.value_type[idx], self.bit_number[idx], self.id[idx])

                # Если адрес регистра такой же как у предыдущего и не такой, как у следующего
                elif (self.reg_address[idx] == self.reg_address[idx - 1]) and (
                        self.reg_address[idx] != self.reg_address[idx + 1]):
                    print('elif-2')
                    self.append_data(self.reg_address[idx], self.query_quantity[idx],
                                     self.value_type[idx], self.bit_number[idx], self.id[idx])
                    self.append_second_data(self.start_register, self.read_quantity, self.reg_type[idx])
                    self.start_register = self.reg_address[idx + 1]
                    self.read_quantity = self.query_quantity[idx + 1]
                # Любая иная ситуация
                else:
                    print('else-1')

                    if (self.reg_address[idx] - self.query_quantity[idx - 1] == self.reg_address[idx - 1]) and \
                            (self.reg_type[idx] == self.reg_type[idx - 1]):

                        print('if-2')
                        self.append_data(self.reg_address[idx], self.query_quantity[idx],
                                         self.value_type[idx], self.bit_number[idx], self.id[idx])
                        self.append_second_data(self.start_register, self.read_quantity, self.reg_type[idx])
                        self.start_register = self.reg_address[idx + 1]
                        self.read_quantity = self.query_quantity[idx + 1]
                    else:
                        print('else-2')
                        self.append_data(self.reg_address[idx], self.query_quantity[idx],
                                         self.value_type[idx], self.bit_number[idx], self.id[idx])
                        self.append_second_data(self.start_register, self.query_quantity[idx], self.reg_type[idx])
                        self.start_register = self.reg_address[idx + 1]
                        self.read_quantity = self.query_quantity[idx + 1]
            else:
                print('else-3')
                if self.reg_address[idx] - self.query_quantity[idx - 1] == self.reg_address[idx - 1] and \
                        self.reg_type[idx] == self.reg_type[idx - 1]:
                    print('if-3')
                   # self.append_second_data(self.start_register, self.read_quantity, self.reg_type[idx])
                    self.append_data(self.reg_address[idx], self.query_quantity[idx],
                                     self.value_type[idx], self.bit_number[idx], self.id[idx])
                else:
                    print('else-4')
                    self.append_data(self.reg_address[idx], self.query_quantity[idx],
                                     self.value_type[idx], self.bit_number[idx], self.id[idx])
                    self.read_quantity = self.query_quantity[idx]

        self.append_second_data(self.start_register, self.read_quantity, self.reg_type[idx])
        return self.return_dict


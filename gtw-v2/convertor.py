from loguru import logger
import struct

FAULT_VALUE = 'fault'


class Convertor:
    def __init__(self, signals, data_values):
        self.index_data_value = None
        self.i = None
        self.signals = signals
        self.data_values = data_values
        self.reg_address = signals['reg_address']
        self.bit_number = signals['bit_number']
        self.value_type = signals['value_type']
        self.present_value = signals['present_value']
        self.uuid = signals['name']
        self.scale = signals['scale']
        self.read_data = 0

    #  print(len(data_values))
    def convert_new(self):
        count = len(self.uuid)
        self.i = 0
        self.index_data_value = 0
        while self.i < count:
            # print(self.i)
            if self.bit_number[self.i] == 'None' or (
                    self.bit_number[self.i] != 'None' and self.value_type[self.i] != 'bool'):
                if self.value_type[self.i] == 'int16':
                    #  print(self.value_type[self.i])
                    self._value_int16()

                elif self.value_type[self.i] == 'int32':
                    #  print(self.value_type[self.i])

                    self._value_int32()
                elif self.value_type[self.i] == 'uint16':
                    #  print(self.value_type[self.i])
                    self._value_uint16()
                elif self.value_type[self.i] == 'uint32':
                    #    print(self.value_type[self.i])
                    self._value_uint32()
                elif self.value_type[self.i] == 'bool':
                    #   print(self.value_type[self.i])
                    self._value_bool()
                elif self.value_type[self.i] == 'float':
                    #   print(self.value_type[self.i])
                    self._value_float()
            elif self.value_type[self.i] == 'bool' and self.bit_number[self.i] != 'None':
                # print(self.value_type[self.i])
                self._value_bit()
        logger.debug(f"Signals length {len(self.signals['name'])}  Values length {len(self.signals['present_value'])}")
        return self.signals

    def _value_int16(self):
        self.add_quantity = 1
        if isinstance(self.data_values[self.index_data_value:self.index_data_value + 1][0], str):
            self.present_value.append(FAULT_VALUE)
        else:
            pv = to_int16(self.data_values[self.index_data_value:self.index_data_value + 1][0])
            #   print(pv * float(self.scale[self.i]))
            self.present_value.append(pv * float(self.scale[self.i]))
        self.i += self.add_quantity
        self.index_data_value += self.add_quantity

    def _value_int32(self):
        self.add_quantity = 2
        big = self.data_values[self.index_data_value:self.index_data_value + 1][0]
        little = self.data_values[self.index_data_value + 1:self.index_data_value + 2][0]
        if big == FAULT_VALUE or little == FAULT_VALUE:
            self.present_value.append(FAULT_VALUE)
        else:
            pv = to_int32([big, little])
            #  print(pv * float(self.scale[self.i]))
            self.present_value.append(pv * float(self.scale[self.i]))
        self.index_data_value += self.add_quantity
        self.i += 1

    def _value_uint16(self):
        self.add_quantity = 1
        if isinstance(self.data_values[self.index_data_value:self.index_data_value + 1][0], str):
            self.present_value.append(FAULT_VALUE)
        else:
            pv = self.data_values[self.index_data_value:self.index_data_value + 1][0]
            #  print(pv * float(self.scale[self.i]))
            self.present_value.append(pv * float(self.scale[self.i]))
        self.index_data_value += self.add_quantity
        self.i += 1

    def _value_uint32(self):
        self.add_quantity = 2
        print(self.signals['name'][self.i])
        big = self.data_values[self.index_data_value:self.index_data_value + 1][0]
        little = self.data_values[self.index_data_value + 1:self.index_data_value + 2][0]
        if big == FAULT_VALUE or little == FAULT_VALUE:
            self.present_value.append(FAULT_VALUE)
        else:
            pv = to_int32([big, little])
            #  print(pv * float(self.scale[self.i]))
            self.present_value.append(pv * float(self.scale[self.i]))
        self.index_data_value += self.add_quantity
        self.i += 1

    def _value_float(self):
        self.add_quantity = 2
        big = self.data_values[self.index_data_value:self.index_data_value + 1][0]
        little = self.data_values[self.index_data_value + 1:self.index_data_value + 2][0]
        if big == FAULT_VALUE or little == FAULT_VALUE:
            self.present_value.append(FAULT_VALUE)
        else:
            #    print(big, "  ", little)
            pv = to_float32([big, little])
            #  print(pv * float(self.scale[self.i]))
            #  print(pv)
            self.present_value.append(pv * float(self.scale[self.i]))
        self.index_data_value += self.add_quantity
        self.i += 1

    def _value_bool(self):
        self.add_quantity = 1
        if isinstance(self.data_values[self.index_data_value:self.index_data_value + 1][0], str):
            self.present_value.append(FAULT_VALUE)
        else:

            pv = to_bool(self.data_values[self.index_data_value:self.index_data_value + 1][0], self.bit_number[self.i])
            self.present_value.append(pv)
        self.index_data_value += self.add_quantity
        self.i += 1

    def _value_bit(self):
        self.add_quantity = 1
        if self.reg_address[self.i] != self.reg_address[self.i + 1]:
            pv = to_bool(self.data_values[self.index_data_value:self.index_data_value + 1][0], self.bit_number[self.i])

            self.present_value.append(pv)
            self.i += 1
        while self.reg_address[self.i] == self.reg_address[self.i + 1] or self.reg_address[self.i] == \
                self.reg_address[self.i - 1]:
            if self.data_values[self.index_data_value:self.index_data_value + 1][0] == FAULT_VALUE:
                self.present_value.append(FAULT_VALUE)
            else:
                pv = to_bool(self.data_values[self.index_data_value:self.index_data_value + 1][0],
                             self.bit_number[self.i])
                self.present_value.append(pv)
            self.i += 1
        self.index_data_value += self.add_quantity


def to_bool(values, bit_number):
    if values == 'fault':
        return 'fault'
    else:
        if bit_number == 'None':
            if values:
                return True
            else:
                return False
        else:
            bv = to_16bit_array(values)
            if int(bv[bit_number]) == 1:
                return True
            else:
                return False


def to_16bit_array(value):
    bin_value = bin(value)[2:]
    if len(bin_value) != 16:
        zero_array = ""
        count = 16 - len(bin_value)
        i = 0
        while i < count:
            i += 1
            zero_array += '0'
        zero_array += bin_value
        return zero_array
    else:
        return bin_value


def to_int16(value):
    order = {'big': '>', 'little': '<'}
    types = {'int16': 'h', 'uint16': 'H', 'int32': 'i', 'uint32': 'I', 'float32': 'f', 'int64': 'l', 'uint64': 'L',
             'float64': 'd'}
    if isinstance(value, int):
        in_value = struct.pack(f"{order['big']}{types['uint16']}", value)
        out_value = struct.unpack(f"{order['big']}{types['int16']}", in_value)
        #  print(out_value[0])
        return out_value[0]
    else:
        return False


def to_uint32(value):
    order = {'big': '>', 'little': '<'}
    types = {'int16': 'h', 'uint16': 'H', 'int32': 'i', 'uint32': 'I', 'float32': 'f', 'int64': 'l', 'uint64': 'L',
             'float64': 'd'}
    if isinstance(value, list) and len(value) == 2:
        in_value = struct.pack(f"{order['big']}2{types['uint16']}", value[0], value[1])
        out_value = struct.unpack(f"{order['big']}{types['uint32']}", in_value)
        #  print(out_value[0])
        return out_value[0]
    else:
        return False


def to_int32(value):
    order = {'big': '>', 'little': '<'}
    types = {'int16': 'h', 'uint16': 'H', 'int32': 'i', 'uint32': 'I', 'float32': 'f', 'int64': 'l', 'uint64': 'L',
             'float64': 'd'}
    if isinstance(value, list) and len(value) == 2:
        in_value = struct.pack(f"{order['big']}2{types['uint16']}", value[0], value[1])
        out_value = struct.unpack(f"{order['big']}{types['int32']}", in_value)
        #  print(out_value[0])
        return out_value[0]
    else:
        return False


def to_float32(values):
    order = {'big': '>', 'little': '<'}
    types = {'int16': 'h', 'uint16': 'H', 'int32': 'i', 'uint32': 'I', 'float32': 'f', 'int64': 'l', 'uint64': 'L',
             'float64': 'd'}
    if isinstance(values, list) and len(values) == 2:
        in_value = struct.pack(f"{order['big']}2{types['uint16']}", values[0], values[1])
        out_value = struct.unpack(f"{order['big']}{types['float32']}", in_value)
        #  print(out_value[0])
        return out_value[0]
    else:
        return False

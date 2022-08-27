from loguru import logger
import math
import struct

FAULT_VALUE = 'fault'


def to_bool(values, bit_number):
    #  print(bit_number, type(bit_number))
    if bit_number == 65.0:
        #  print("IN BOOL")
        if values:
            return True
        else:
            return False
    else:
        #   print("IN BIT")
        bv = to_16bit_array(values)
        #   print(bv)
        if int(bv[int(bit_number)]) == 1:
            return True
        else:
            return False


def to_16bit_array(value):
    bin_value = bin(value[0])[2:]
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


def to_int(values):
    if values[0] >= 0:
        return values[0]
    else:
        return abs(values[0]) + 32768


def to_float(values):
    b = bytearray(4)
    b[0] = values[0] & 0xff
    b[1] = (values[0] & 0xff00) >> 8
    b[2] = (values[1] & 0xff)
    b[3] = (values[1] & 0xff00) >> 8
    return_value = struct.unpack('<f', b)  # little Endian
    return return_value[0]


def from_float_32(registers):
    """
    Convert 32 Bit real Value to two 16 Bit Value to send as Modbus Registers
    floatValue: Value to be converted
    return: 16 Bit Register values int[]
    """
    b = bytearray(4)
    b[0] = registers[0] & 0xff
    b[1] = (registers[0] & 0xff00) >> 8
    b[2] = (registers[1] & 0xff)
    b[3] = (registers[1] & 0xff00) >> 8
    return_value = struct.unpack('<f', b)  # little Endian
    return return_value[0]


class Convertor:
    def __init__(self, signals, data_values):
        self.signals = signals
        self.data_values = data_values
        self.reg_address = signals['reg_address']
        self.bit_number = signals['bit_number']
        self.value_type = signals['value_type']
        self.present_value = signals['present_value']
        self.uuid = signals['name']
        self.scale = signals['scale']

    def convert(self):
        count = len(self.uuid)
        i = 0
        index_data_value = 0
        while i < count:
            if math.isnan(self.bit_number[i]) or (math.isnan(self.bit_number[i]) and self.value_type[i] != 'bool'):
                # Запись значения типа INT
                if self.value_type[i] == 'int':
                    add_quantity = 1
                    if self.data_values[index_data_value:index_data_value + 1] == FAULT_VALUE:
                        self.present_value.append(FAULT_VALUE)
                    else:
                        pv = to_int(self.data_values[index_data_value:index_data_value + 1])
                        self.present_value.append(pv * self.scale[i])
                    i += add_quantity
                    index_data_value += add_quantity
                # Запись значения типа UINT
                elif self.value_type[i] == 'uint':
                    add_quantity = 1
                    if self.data_values[index_data_value:index_data_value + 1] == FAULT_VALUE:
                        self.present_value.append(FAULT_VALUE)
                    else:
                        pv = self.data_values[index_data_value:index_data_value + 1]
                        self.present_value.append(pv[0] * self.scale[i])
                    index_data_value += add_quantity
                    i += 1
                    # Запись значения типа BOOL
                elif self.value_type[i] == 'bool':
                    add_quantity = 1
                    if self.data_values[index_data_value:index_data_value + 1] == FAULT_VALUE:
                        self.present_value.append(FAULT_VALUE)
                    else:
                        pv = to_bool(self.data_values[index_data_value:index_data_value + 1], 65.0)
                        self.present_value.append(pv)
                    index_data_value += add_quantity
                    i += 1
                    # Запись значения типа FLOAT
                elif self.value_type[i] == 'float':
                    add_quantity = 2
                    big = self.data_values[index_data_value:index_data_value + 1]
                    little = self.data_values[index_data_value + 1:index_data_value + 2]
                    if big == FAULT_VALUE or little == FAULT_VALUE:
                        self.present_value.append(FAULT_VALUE)
                    else:
                        pv = to_float([big[0], little[0]])
                        self.present_value.append(pv * self.scale[i])
                    index_data_value += add_quantity
                    i += 1
            elif self.value_type[i] == 'bool' and not math.isnan(self.bit_number[i]):
                add_quantity = 1
                while self.reg_address[i] == self.reg_address[i + 1] or self.reg_address[i] == self.reg_address[i - 1]:
                    if self.data_values[index_data_value:index_data_value + 1] == FAULT_VALUE:
                        self.present_value.append(FAULT_VALUE)
                    else:
                        pv = to_bool(self.data_values[index_data_value:index_data_value + 1], self.bit_number[i])
                        self.present_value.append(pv)
                    i += 1
                index_data_value += add_quantity
        logger.debug(f"Signals length {len(self.signals['name'])}  Values length {len(self.signals['present_value'])}")
        return self.signals

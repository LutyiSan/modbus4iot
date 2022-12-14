from pymodbus.constants import Endian
from pymodbus.payload import BinaryPayloadDecoder


class Convertor:

    def __init__(self, signals, data_values, multi_read):
        self.multi_read = multi_read
        self.index_data_value = None
        self.i = None
        self.signals = signals
        self.data_values = data_values
        self.reg_address = signals['reg_address']
        self.bit_number = signals['bit_number']
        self.value_type = signals['value_type']
        self.present_value = signals['present_value']
        self.name = signals['name']
        self.scale = signals['scale']
        self.read_data = 0
        self.fault_value = 'fault'

    def convert(self):
        count = len(self.name)
        self.i = 0
        self.index_data_value = 0
        while self.i < count:
            if self.value_type[self.i] != 'bool':
                if 'int' in self.value_type[self.i]:
                    self._value_int()
                elif 'uint' in self.value_type[self.i]:
                    self._value_uint()
                elif 'float' in self.value_type[self.i]:
                    self._value_float()
            elif self.value_type[self.i] == 'bool' and self.bit_number[self.i] is None:
                self._value_bool()
            elif self.value_type[self.i] == 'bool' and self.bit_number[self.i] is not None:
                if self.multi_read:
                    self._value_mbit()
                else:
                    self._value_bit()
        return self.signals

    def _value_int(self):
        if isinstance(self.data_values[self.index_data_value], str):
            self.present_value.append(self.fault_value)
        else:
            if '16' in self.value_type[self.i]:
                pv = Convertor.to_int16(self.data_values[self.index_data_value])
                self.present_value.append(pv * float(self.scale[self.i]))
                self.i += 1
                self.index_data_value += 1
            elif '32' in self.value_type[self.i]:
                pv = Convertor.to_int32(self.data_values[self.index_data_value:self.index_data_value + 2])
                self.present_value.append(pv * float(self.scale[self.i]))
                self.i += 1
                self.index_data_value += 2
            elif '64' in self.value_type[self.i]:
                pv = Convertor.to_int64(self.data_values[self.index_data_value:self.index_data_value + 4])
                self.present_value.append(pv * float(self.scale[self.i]))
                self.i += 1
                self.index_data_value += 4

    def _value_uint(self):
        if isinstance(self.data_values[self.index_data_value], str):
            self.present_value.append(self.fault_value)
        else:
            if '16' in self.value_type[self.i]:
                pv = Convertor.to_uint16(self.data_values[self.index_data_value])
                self.present_value.append(pv * float(self.scale[self.i]))
                self.i += 1
                self.index_data_value += 1
            elif '32' in self.value_type[self.i]:
                pv = Convertor.to_uint32(self.data_values[self.index_data_value:self.index_data_value + 2])
                self.present_value.append(pv * float(self.scale[self.i]))
                self.i += 1
                self.index_data_value += 2
            elif '64' in self.value_type[self.i]:
                pv = Convertor.to_uint64(self.data_values[self.index_data_value:self.index_data_value + 4])
                self.present_value.append(pv * float(self.scale[self.i]))
                self.i += 1
                self.index_data_value += 4

    def _value_float(self):
        if isinstance(self.data_values[self.index_data_value], str):
            self.present_value.append(self.fault_value)
        else:
            if '16' in self.value_type[self.i]:
                pv = Convertor.to_float16(self.data_values[self.index_data_value])
                self.present_value.append(pv * float(self.scale[self.i]))
                self.i += 1
                self.index_data_value += 1
            elif '32' in self.value_type[self.i]:
                pv = Convertor.to_float32(self.data_values[self.index_data_value:self.index_data_value + 2])

                self.present_value.append(pv * float(self.scale[self.i]))
                self.i += 1
                self.index_data_value += 2
            elif '64' in self.value_type[self.i]:
                pv = Convertor.to_float64(self.data_values[self.index_data_value:self.index_data_value + 4])
                self.present_value.append(pv * float(self.scale[self.i]))
                self.i += 1
                self.index_data_value += 4

    @staticmethod
    def to_uint16(value: int, inverse=False) -> int or None:
        if inverse:
            bo = Endian.Little
        else:
            bo = Endian.Big
        if isinstance(value, int):
            decoder = BinaryPayloadDecoder.fromRegisters([value], byteorder=bo, wordorder=Endian.Big)
            return decoder.decode_16bit_uint()
        else:
            return None

    @staticmethod
    def to_int16(value: int, inverse=False) -> int or None:
        if inverse:
            bo = Endian.Little
        else:
            bo = Endian.Big
        if isinstance(value, int):
            decoder = BinaryPayloadDecoder.fromRegisters([value], byteorder=bo, wordorder=Endian.Big)
            return decoder.decode_16bit_int()
        else:
            return None

    @staticmethod
    def to_int32(values: list[int], inverse=False) -> int or None:
        if inverse:
            wo = Endian.Little
        else:
            wo = Endian.Big
        if isinstance(values, list) and len(values) == 2:
            for i in values:
                if not isinstance(i, int):
                    return None
                else:
                    decoder = BinaryPayloadDecoder.fromRegisters(values, byteorder=Endian.Big, wordorder=wo)
                    return decoder.decode_32bit_int()
        else:
            return None

    @staticmethod
    def to_int64(values: list[int], inverse=False) -> int or None:
        if inverse:
            wo = Endian.Little
        else:
            wo = Endian.Big
        if isinstance(values, list) and len(values) == 4:
            for i in values:
                if not isinstance(i, int):
                    return None
                else:
                    decoder = BinaryPayloadDecoder.fromRegisters(values, byteorder=Endian.Big, wordorder=wo)
                    return decoder.decode_64bit_int()
        else:
            return None

    @staticmethod
    def to_uint32(values: list[int], inverse=False) -> int or None:
        if inverse:
            wo = Endian.Little
        else:
            wo = Endian.Big

        if isinstance(values, list) and len(values) == 2:
            for i in values:
                if not isinstance(i, int):
                    return None
            else:
                decoder = BinaryPayloadDecoder.fromRegisters(values, byteorder=Endian.Big, wordorder=wo)
                return decoder.decode_32bit_uint()
        else:
            return None

    @staticmethod
    def to_uint64(values: list[int], inverse=False) -> int or None:
        if inverse:
            wo = Endian.Little
        else:
            wo = Endian.Big
        if isinstance(values, list) and len(values) == 4:
            for i in values:
                if not isinstance(i, int):
                    return None
                else:
                    decoder = BinaryPayloadDecoder.fromRegisters(values, byteorder=Endian.Big, wordorder=wo)
                    return decoder.decode_64bit_uint()
        else:
            return None

    @staticmethod
    def to_float16(values: int, inverse=False) -> float or None:
        if inverse:
            bo = Endian.Little
        else:
            bo = Endian.Big
        if isinstance(values, int):
            decoder = BinaryPayloadDecoder.fromRegisters([values], byteorder=bo, wordorder=Endian.Little)
            return decoder.decode_16bit_float()
        else:
            return None

    @staticmethod
    def to_float32(values: list[int], inverse=False) -> float or None:
        if not inverse:
            wo = Endian.Big
        else:
            wo = Endian.Little
        if isinstance(values, list) and len(values) == 2:
            for i in values:
                if not isinstance(i, int):
                    return None
                else:
                    decoder = BinaryPayloadDecoder.fromRegisters(values, byteorder=Endian.Big, wordorder=wo)
                    return decoder.decode_32bit_float()
        else:
            return None

    @staticmethod
    def to_float64(values: list[int], inverse=False) -> float or None:
        if inverse:
            wo = Endian.Big
        else:
            wo = Endian.Little
        if isinstance(values, list) and len(values) == 4:
            for i in values:
                if not isinstance(i, int):
                    return None
                else:
                    decoder = BinaryPayloadDecoder.fromRegisters(values, byteorder=Endian.Big, wordorder=wo)
                    return decoder.decode_64bit_float()
        else:
            return None

    def _value_bool(self):

        if isinstance(self.data_values[self.index_data_value], str):
            self.present_value.append(self.fault_value)
        else:
            pv = Convertor.to_bool(self.data_values[self.index_data_value])
            self.present_value.append(pv)
        self.index_data_value += 1
        self.i += 1

    def _value_bit(self):
        pv = Convertor.to_bit(self.data_values[self.index_data_value], self.bit_number[self.i])
        self.present_value.append(pv)
        self.index_data_value += 1
        self.i += 1

    def _value_mbit(self):
        if self.reg_address[self.i] != self.reg_address[self.i + 1] and self.reg_address[self.i] \
                != self.reg_address[self.i - 1]:
            pv = Convertor.to_bit(self.data_values[self.index_data_value], self.bit_number[self.i])
            self.present_value.append(pv)
            self.index_data_value += 1
            self.i += 1
        else:
            address = self.reg_address[self.i]
            while address == self.reg_address[self.i]:
                pv = Convertor.to_bit(self.data_values[self.index_data_value], self.bit_number[self.i])
                self.present_value.append(pv)
                self.i += 1
            self.index_data_value += 1

    @staticmethod
    def to_bool(value):
        if value is None:
            return None
        else:
            if value:
                return True
            else:
                return False

    @staticmethod
    def to_bit(value, bit):
        #  print(bit)
        if value is None:
            return None
        else:
            bv = Convertor.to_16bit_array(value)
            if int(bv[bit]) == 1:
                return True
            else:
                return False

    @staticmethod
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

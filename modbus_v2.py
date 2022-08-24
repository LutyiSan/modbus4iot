from easymodbus import modbusClient
import struct
from loguru import logger


class TCPClient:
    def __init__(self, ip_address, tcp_port):
        self.client = modbusClient.ModbusClient(ip_address, tcp_port)

    def connection(self):
        try:
            self.client.connect()
            logger.debug("Modbus READY connection")
            return True
        except Exception as e:
            logger.exception("FAIL connect to device\n", e)
            return False

    def reader(self, device):
        logger.info("Start reading ......")
        query_count = len(device['signal_name']) - 1
        idx = -1
        while idx < query_count:
            idx += 1
            if device['registers_type'][idx] == "holding registers":
                device['present_value'][idx] = verifier(self.read_hr(device['register_address'][idx], device['quantity'][idx]),
                         device['quantity'][idx],device['value_type'][idx],
                         device['scale'][idx],device['bit_number'][idx])

            elif device['registers_type'][idx] == "input registers":
                device['present_value'][idx] = verifier(self.read_ir(device['register_address'][idx], device['quantity'][idx]),
                         device['quantity'][idx], device['value_type'][idx],
                         device['scale'][idx], device['bit_number'][idx])
            elif device['registers_type'][idx] == "coils":
                device['present_value'][idx] = verifier(self.read_coils(device['register_address'][idx], device['quantity'][idx]),
                         device['quantity'][idx], device['value_type'][idx],
                         device['scale'][idx], device['bit_number'][idx])
            elif device['registers_type'][idx] == "discrete inputs":
                device['present_value'][idx] = verifier(self.read_di(device['register_address'][idx], device['quantity'][idx]),
                         device['quantity'][idx], device['value_type'][idx],
                         device['scale'][idx], device['bit_number'][idx])
        logger.info(".....STOP reading")
        return device

    def read_hr(self, reg_number, quantity):
        try:
            result = self.client.read_holdingregisters(reg_number, quantity)

            return result
        except Exception as e:
            logger.exception("Can't Read registers\n", e)
            return False

    def read_ir(self, reg_number, quantity):
        try:
            result = self.client.read_inputregisters(reg_number, quantity)
            return result
        except Exception as e:
            logger.exception("Can't Read registers\n", e)
            return False

    def read_coils(self, reg_number, quantity):
        try:
            result = self.client.read_coils(reg_number, quantity)
            return result
        except Exception as e:
            logger.exception("Can't Read registers\n", e)
            return False

    def read_di(self, reg_number, quantity):
        try:
            result = self.client.read_coils(reg_number, quantity)
            return result
        except Exception as e:
            logger.exception("Can't Read registers\n", e)
            return False

    def disconnect(self):
        try:
            self.client.close()
            logger.debug("Connection closed")
        except Exception as e:
            logger.exception("Can't close connection", e)


def read_verifier(values, quantity):
    return_values = []
    if isinstance(values, list) and (len(values) == quantity):
        return values
    else:
        for i in range(quantity):
            return_values.append("fault")
        return return_values


def convert(values, data_type, scale, bit_number):
    return_data = None
    if data_type == 'bool':
        return_data = to_bool(values, bit_number)
    elif data_type == "uint":
        return values[0] * scale
    elif data_type == "int":
        return_data = to_int(values) * scale
    elif data_type == "float":
        return_data = to_float(values) * scale
    return return_data


def to_bool(values, bit_number):
    if not isinstance(bit_number, int):
        if values[0]:
            return True
        else:
            return False
    elif isinstance(bit_number, int):
        bv = to_16bit_array(values[0])
        if int(bv) == 1:
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


def to_int(values):
    if values[0] >= 0:
        return values[0]
    else:
        return (abs(values[0]) + 32768)


def to_float(values):
    b = bytearray(4)
    b[0] = values[0] & 0xff
    b[1] = (values[0] & 0xff00) >> 8
    b[2] = (values[1] & 0xff)
    b[3] = (values[1] & 0xff00) >> 8
    return_value = struct.unpack('<f', b)  # little Endian
    return return_value[0]


def verifier(reading_data, quantity, data_type, scale, bit_number):
    rd = "fault"
    vv = read_verifier(reading_data, quantity)
    if 'fault' in vv:
        return rd
    else:
        rd = convert(vv, data_type, scale, bit_number)
        return rd





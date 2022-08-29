from pymodbus.client.sync import ModbusTcpClient as ModbusClient
from loguru import logger
from func_timeout import func_set_timeout
from gtw.env import READ_TIMEOUT


UNIT = 0x1
FAULT_VALUE = 'fault'


class TCPClient:
    def __init__(self, ip_address, tcp_port):
        self.client = ModbusClient(ip_address, port=tcp_port, timeout=5)

    def connection(self):
        try:
            self.client.connect()
            logger.debug("Modbus READY connection")
            return True
        except Exception as e:
            logger.exception("FAIL connect to device\n", e)
            return False

    @func_set_timeout(READ_TIMEOUT)
    def read_single(self, device):
        device['present_value'] = []
        pv_list = []
        logger.info("Start reading ......")
        query_count = len(device['name']) - 1
        idx = -1
        while idx < query_count:
            idx += 1
            if device['reg_type'][idx] == "hr":
                pv = read_verifier(self.read_hr(device['reg_address'][idx], device['quantity'][idx]),
                                   device['quantity'][idx])
                pv_list.append(pv)
            elif device['reg_type'][idx] == "ir":
                pv = read_verifier(self.read_ir(device['reg_address'][idx], device['quantity'][idx]),
                                   device['quantity'][idx])
                pv_list.append(pv)
            elif device['reg_type'][idx] == "co":
                pv = read_verifier(self.read_coils(device['reg_address'][idx], device['quantity'][idx]),
                                   device['quantity'][idx])
                pv_list.append(pv)
            elif device['reg_type'][idx] == "di":
                pv = read_verifier(self.read_di(device['reg_address'][idx], device['quantity'][idx]),
                                   device['quantity'][idx])
                pv_list.append(pv)
        logger.info(".....STOP reading")
        data_list = []
        for i in pv_list:
            for ii in i:
                data_list.append(ii)
        return device, data_list

    @func_set_timeout(READ_TIMEOUT)
    def read_multiple(self, signals):
        pv_list = []
        data_list = []
        count = len(signals['start_address'])
        idx = -1
        while idx < count - 1:
            idx += 1
            if signals['reg_type'][idx] == "hr":
                pv = read_verifier(self.read_hr(signals['start_address'][idx], signals['read_quantity'][idx]),
                                   signals['read_quantity'][idx])
                pv_list.append(pv)
            elif signals['reg_type'][idx] == "ir":
                pv_list.append(
                    read_verifier(self.read_ir(signals['start_address'][idx], signals['read_quantity'][idx]),
                                  signals['read_quantity'][idx]))
            elif signals['reg_type'][idx] == "coil":
                pv_list.append(
                    read_verifier(self.read_coils(signals['start_address'][idx], signals['read_quantity'][idx]),
                                  signals['read_quantity'][idx]))
            elif signals['reg_type'][idx] == "di":
                pv_list.append(
                    read_verifier(self.read_di(signals['start_address'][idx], signals['read_quantity'][idx]),
                                  signals['read_quantity'][idx]))
        # logger.info(f"Reading list{pv_list}")
        logger.info(".....STOP reading")
        for i in pv_list:
            for ii in i:
                data_list.append(ii)
        return signals, data_list

    def read_hr(self, reg_number, quantity):

        try:
            result = self.client.read_holding_registers(reg_number, quantity, unit=UNIT)

            return result.registers
        except Exception as e:
            logger.exception("Can't Read registers\n", e)
            return False

    def read_ir(self, reg_number, quantity):
        try:
            result = self.client.read_input_registers(reg_number, quantity, unit=UNIT)
            return result.registers
        except Exception as e:
            logger.exception("Can't Read registers\n", e)
            return False

    def read_coils(self, reg_number, quantity):
        try:
            result = self.client.read_coils(reg_number, quantity, unit=UNIT)
            return result.bits
        except Exception as e:
            logger.exception("Can't Read registers\n", e)
            return False

    def read_di(self, reg_number, quantity):
        try:
            result = self.client.read_discrete_inputs(reg_number, quantity, unit=UNIT)
            return result.bits
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
        logger.info(values)
        return values
    else:
        for i in range(quantity):
            return_values.append(FAULT_VALUE)
        logger.info(return_values)
        return return_values

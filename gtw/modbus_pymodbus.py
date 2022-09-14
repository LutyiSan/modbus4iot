from pymodbus.client.sync import ModbusTcpClient as ModbusClient
from loguru import logger


class TCPClient:
    UNIT = 0x1
    FAULT_VALUE = 'fault'
    mblog = logger

    def connection(self, ip_address, tcp_port=502, timeout=3):
        try:
            self.client = ModbusClient(ip_address, port=tcp_port, timeout=timeout)
            if self.client.connect():
                self.mblog.debug(f"READY connection {ip_address}")
                return True
            else:
                self.mblog.error(f"FAIL connection {ip_address}")
                return False
        except Exception as e:
            self.mblog.exception(f"FAIL connect {ip_address}", e)
            return False

    def read_single(self, device):
        pv = None
        device['present_value'] = []
        pv_list = []
        logger.info("Start reading ......")
        query_count = len(device['name']) - 1
        idx = -1
        while idx < query_count:
            logger.debug(device['reg_address'][idx])
            idx += 1
            if device['reg_type'][idx] == "hr":
                pv = TCPClient.read_verifier(self.__read_hr(device['reg_address'][idx], device['quantity'][idx]),
                                             device['quantity'][idx])
                pv_list.append(pv)
            elif device['reg_type'][idx] == "ir":
                pv = TCPClient.read_verifier(self.__read_ir(device['reg_address'][idx], device['quantity'][idx]),
                                             device['quantity'][idx])
                pv_list.append(pv)
            elif device['reg_type'][idx] == "co":
                pv = TCPClient.read_verifier(self.__read_coils(device['reg_address'][idx], device['quantity'][idx]),
                                             device['quantity'][idx])
                pv_list.append(pv)
            elif device['reg_type'][idx] == "di":
                pv = self.__read_di(device['reg_address'][idx], device['quantity'][idx])
                if isinstance(pv, list):
                    if False in pv:
                        pv_list.append([False])
                    else:
                        pv_list.append([True])
                else:
                    pv_list.append(None)
            logger.debug(pv)
        self.mblog.info(".....STOP reading")
        data_list = []
        for group in pv_list:
            for value in group:
                data_list.append(value)
        logger.debug(data_list)

        return device, data_list

    def read_multiple(self, signals):
        pv_list = []
        data_list = []
        count = len(signals['start_address'])
        idx = -1
        while idx < count - 1:

            idx += 1
            if signals['reg_type'][idx] == "hr":
                pv = TCPClient.read_verifier(
                    self.__read_hr(signals['start_address'][idx], signals['read_quantity'][idx]),
                    signals['read_quantity'][idx])
                self.mblog.debug(f"From start register {signals['start_address'][idx]}")
                pv_list.append(pv)
            elif signals['reg_type'][idx] == "ir":
                pv_list.append(
                    TCPClient.read_verifier(
                        self.__read_ir(signals['start_address'][idx], signals['read_quantity'][idx]),
                        signals['read_quantity'][idx]))
                self.mblog.debug(f"From start register {signals['start_address'][idx]}")
            elif signals['reg_type'][idx] == "coil":
                pv_list.append(
                    TCPClient.read_verifier(
                        self.__read_coils(signals['start_address'][idx], signals['read_quantity'][idx]),
                        signals['read_quantity'][idx]))
                self.mblog.debug(f"From start register {signals['start_address'][idx]} read {pv}")
            elif signals['reg_type'][idx] == "di":
                pv_list.append(
                    TCPClient.read_verifier(
                        self.__read_di(signals['start_address'][idx], signals['read_quantity'][idx]),
                        signals['read_quantity'][idx]))
                self.mblog.debug(f"From start register {signals['start_address'][idx]}")
        logger.info(".....STOP reading")
        for group in pv_list:
            for value in group:
                data_list.append(value)

        return signals, data_list

    def __read_hr(self, reg_number, quantity):

        try:
            result = self.client.read_holding_registers(reg_number, quantity, unit=self.UNIT)

            return result.registers
        except Exception as e:
            self.mblog.exception("Can't Read registers\n", e)
            return False

    def __read_ir(self, reg_number, quantity):
        try:
            result = self.client.read_input_registers(reg_number, quantity, unit=self.UNIT)
            return result.registers
        except Exception as e:
            self.mblog.exception("Can't Read registers\n", e)
            return False

    def __read_coils(self, reg_number, quantity):
        try:
            result = self.client.read_coils(reg_number, quantity, unit=self.UNIT)
            return result.bits
        except Exception as e:
            self.mblog.exception("Can't Read registers\n", e)
            return False

    def __read_di(self, reg_number, quantity):

        try:
            result = self.client.read_discrete_inputs(reg_number, quantity, unit=self.UNIT)
            logger.debug(result.bits[0])
            return result.bits
        except Exception as e:
            self.mblog.exception("Can't Read registers\n", e)
            return False

    def disconnect(self):
        try:
            self.client.close()
            logger.debug("Connection closed")
        except Exception as e:
            logger.exception("Can't close connection", e)

    @staticmethod
    def read_verifier(values, quantity):
        return_values = []
        if isinstance(values, list) and (len(values) == quantity):
            # logger.info(values)
            return values
        else:
            for i in range(quantity):
                return_values.append(None)
            # logger.info(return_values)
            return return_values

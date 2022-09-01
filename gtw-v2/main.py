from loguru import logger
from func_timeout import FunctionTimedOut
import time
from modbus_pymodbus import TCPClient
from convertor import Convertor
from mqtt import MyMQTT
from gtw.env import *
from gtw.grouper import Grouper, csv_to_dict


class GTW:
    def __init__(self):
        self.device = None
        self.result = None
        self.mqttclient = MyMQTT()
        self.mqtt_create_state = self.mqttclient.create(USER_NAME, USE_PASSWD)
        self.reading_data = None

    def run_gtw(self):
        logger.info("GTW is running on")
        for device in DEVICE_LIST:
            self.device = csv_to_dict(device, ';')  # Получаем словарь из csv девайса
            if self.device:
                logger.info("Grouping objects...")
                if self.__group_objects(device):
                    if self.__modbus_connect(self.device['device_ip'][0], self.device['port'][0]):
                        if self.__modbus_read(self.device['device_ip'][0], self.signals, self.device):
                            logger.info("Convert reading objects...")
                            cv = Convertor(self.reading_data[0], self.reading_data[1])
                            self.result = cv.convert_new()
                        else:
                            logger.error(f"Some trouble with read registers from device {self.device['device_ip'][0]}")
                else:
                    logger.error(f"{device} with device-data is wrong")
            else:
                logger.error(f"{device} with device-data is wrong")
            self.sent_data()

    def __group_objects(self, device):
        self.grouper = Grouper(device)
        self.signals = self.grouper.grouping()
        q=0
        for qq in self.signals['quantity']:
            q+=qq
        rq = 0
        for rqq in self.signals['quantity']:
            rq += rqq
        print(f" Len quanty {q}  lem read_quanty {rq}")

        return self.signals

    def __modbus_connect(self, ip, port):
        self.client = TCPClient(ip, port)
        return self.client.connection()

    def __modbus_read(self, ip, signals, device):
        if MULTI_READ > 1:
            try:
                logger.info(f"Reading objects from device...{ip}")
                self.reading_data = self.client.read_multiple(signals)
                print(len(self.reading_data[1]))
            except FunctionTimedOut:
                logger.exception("TIMEOUT", FunctionTimedOut)
            self.client.disconnect()
            return self.reading_data
        else:
            try:
                logger.info(f"Reading objects from device...{ip}")
                self.reading_data = self.client.read_single(device)
            except FunctionTimedOut:
                logger.exception("TIMEOUT", FunctionTimedOut)
            self.client.disconnect()
            return self.reading_data

    def sent_data(self):
        if self.result:
            sent_data = dict.fromkeys(self.result['name'])
            idx = -1
            for i in sent_data:
                idx += 1
                sent_data[i] = self.result['present_value'][idx]
            if self.mqttclient.connect(BROKER, BROKER_PORT):
                #  print(self.device)
                self.mqttclient.send(f'{TOPIC}/{self.device["topic"][1]}', sent_data)


def runtime():
    gtw = GTW()
    while True:
        gtw.run_gtw()
        time.sleep(1)


if __name__ == "__main__":
    runtime()

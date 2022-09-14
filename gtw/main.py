import random
from loguru import logger
import time
from modbus_pymodbus import TCPClient
from convertor import Convertor
from mqtt import MyMQTT
from env import *
from grouper import Grouper, csv_to_dict


class GTW:
    gtwlog = logger

    def __init__(self):
        self.device = None
        self.result = None
        self.mqttclient = MyMQTT()
        self.mqtt_create_state = self.mqttclient.create(USER_NAME, USE_PASSWD)
        self.reading_data = None

    def run_gtw(self):
        self.gtwlog.info("GTW is running on")
        for device in DEVICE_LIST:
            self.device = csv_to_dict(device, ';')  # Получаем словарь из csv девайса
            if self.device:
                self.gtwlog.info("Grouping objects...")
                if self.__group_objects(device):
                    if self.__modbus_connect(self.device['device_ip'][0], self.device['port'][0]):
                        if self.__modbus_read(self.device['device_ip'][0], self.signals, self.device):
                            self.gtwlog.info("Convert reading objects...")
                            #     print(self.reading_data[0], self.reading_data[1])
                            cv = Convertor(self.reading_data[0], self.reading_data[1])
                            self.result = cv.convert()
                            self.__sent_data()
                        else:
                            self.gtwlog.error(
                                f"Some trouble with read registers from device {self.device['device_ip'][0]}")
                else:
                    self.gtwlog.error(f"{device} with device-data is wrong")
            else:
                self.gtwlog.error(f"{device} with device-data is wrong")

    def __group_objects(self, device):
        self.grouper = Grouper(device)
        self.signals = self.grouper.grouping()
        return self.signals

    def __modbus_connect(self, ip, port):
        self.client = TCPClient()
        return self.client.connection(ip, port)

    def __modbus_read(self, ip, signals, device):
        if MULTI_READ > 1:
            try:
                self.gtwlog.info(f"Reading objects from device...{ip}")
                self.reading_data = self.client.read_multiple(signals)
            except Exception as e:
                self.gtwlog.exception("TIMEOUT", e)
            self.client.disconnect()
            #  print(len(self.reading_data[1]))

            return self.reading_data
        else:
            try:
                self.gtwlog.info(f"Reading objects from device...{ip}")
                self.reading_data = self.client.read_single(device)
            except Exception as e:
                self.gtwlog.exception("TIMEOUT", e)
            self.client.disconnect()
            return self.reading_data

    def __sent_data(self):
        if self.result:
            # print(len(self.result['present_value']))
            sent_data = dict.fromkeys(self.result['name'])
            idx = -1
            while idx < (len(self.result['name']) - 1):
                idx += 1
                #   logger.info(idx)
                #   logger.info(self.result['present_value'][idx])

                sent_data[self.result['name'][idx]] = self.result['present_value'][idx]
            if self.mqttclient.connect(BROKER, BROKER_PORT):
                self.mqttclient.send(f'{TOPIC}/{self.device["topic"][1]}', sent_data)


def runtime():
    gtw = GTW()
    while True:
        gtw.run_gtw()
        pause = random.uniform(0.3, 1.1)
        time.sleep(pause)


if __name__ == "__main__":
    runtime()

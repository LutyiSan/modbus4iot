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
        self.result = None
        self.mqttclient = MyMQTT()
        self.mqtt_create_state = self.mqttclient.create(USER_NAME, USE_PASSWD)
        self.reading_data = None

    def run_modbus(self):
        logger.info("GTW is running on")
        for i in DEVICE_LIST:
            print(i)
            self.device = csv_to_dict(i, ';')  # Получаем словарь из csv девайса

            if self.device:
                logger.info("Grouping objects...")
               # self.gr = Grouper()

                self.gr = Grouper(i)
                self.signals = self.gr.grouping()

             #   print(self.signals)
                self.client = TCPClient(self.device['device_ip'][0], self.device['port'][0])
                if self.client.connection():
                    if MULTI_READ > 1:
                        try:
                            logger.info(f"Reading objects from device...{self.device['device_ip'][1]}")
                            self.reading_data = self.client.read_multiple(self.signals)
                        except FunctionTimedOut:
                            logger.exception("TIMEOUT", FunctionTimedOut)
                            self.client.disconnect()
                            time.sleep(1)
                    else:
                        try:
                            logger.info("Reading objects from device...")
                            self.reading_data = self.client.read_single(self.device)

                        except FunctionTimedOut:
                            logger.exception("TIMEOUT", FunctionTimedOut)
                            self.client.disconnect()
                            time.sleep(1)
                    if self.reading_data:
                        logger.info("Convert reading objects...")
                        cv = Convertor(self.reading_data[0], self.reading_data[1])
                        self.result = cv.convert()
            self.client.disconnect()
            self.sent_data()

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
        gtw.run_modbus()
        gtw.sent_data()


if __name__ == "__main__":
    runtime()

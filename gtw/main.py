from loguru import logger
from time import time, sleep
from modbus_pymodbus import TCPClient
from convertor import Convertor
from mqtt import MyMQTT
from env import *
from grouper import Grouper, csv_to_dict


def do_devices():
    logger.info("Create device objects from CSV-file(s)...")
    devices_list = []
    if DEVICE_LIST and (len(DEVICE_LIST) > 0):
        for i in DEVICE_LIST:
            d = csv_to_dict(i, ';')
            devices_list.append(d)
    if devices_list:
        logger.info("Created devices from CSV-file(s)")
        return devices_list


class GTW:
    def __init__(self):
        self.mqttclient = MyMQTT()
        logger.info("Create MQTT-client")
        self.mqtt_create_state = self.mqttclient.create(USER_NAME, USE_PASSWD)

    def run_gtw(self, devices_list):
        logger.info("GTW is running on")
        for device in devices_list:
            if device:
                logger.info("Grouping objects...")
                self.__group_objects(device)
                logger.info("Connecting to device...")
                if self.__modbus_connect(device['device_ip'][0], device['port'][0]):
                    if self.__modbus_read(device['device_ip'][0], self.signals, device):
                        logger.info("Convert reading objects...")
                        cv = Convertor(self.reading_data[0], self.reading_data[1], self.reading_data[2])
                        self.__sent_data(device, cv.convert())
                    else:
                        logger.error(f"Some trouble with read registers from device {device['device_ip'][0]}")

    def __group_objects(self, device):
        if MULTI_READ > 1:
            self.grouper = Grouper(device)
            self.signals = self.grouper.grouping()
            return self.signals
        else:
            self.signals = False
            return self.signals

    def __modbus_connect(self, ip, port):
        self.client = TCPClient()
        return self.client.connection(ip, port)

    def __modbus_read(self, ip, signals, device):
        stt = time()
        if MULTI_READ > 1:
            try:
                logger.info(f"Reading objects from device...{ip}")
                self.reading_data = self.client.read_multiple(signals)
            except Exception as e:
                logger.exception("TIMEOUT", e)
            self.client.disconnect()
            stop = time() - stt
            logger.info(f'Time read device {stop}')
            #  print(len(self.reading_data[1]))

            return self.reading_data
        else:
            try:
                logger.info(f"Reading objects from device...{ip}")
                self.reading_data = self.client.read_single(device)
            except Exception as e:
                logger.exception("TIMEOUT", e)
            self.client.disconnect()

            return self.reading_data

    def __sent_data(self, device, result):
        if result:
            sent_data = dict.fromkeys(result['name'])
            idx = -1
            while idx < (len(result['name']) - 1):
                idx += 1
                sent_data[result['name'][idx]] = result['present_value'][idx]
            if self.mqttclient.connect(BROKER, BROKER_PORT):
                self.mqttclient.send(f'{TOPIC}/{device["topic"][1]}', sent_data)


def runtime():
    devices_list = do_devices()
    if devices_list:
        gtw = GTW()
        while True:
            gtw.run_gtw(devices_list)
            sleep(1)
    else:
        logger.error('Wrong DEVICE_LIST! See gtw/env.py...')


if __name__ == "__main__":
    runtime()

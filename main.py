from loguru import logger
from csv_to_dict import get_device_dict
from modbus_v2 import TCPClient
from mqtt import MyMQTT
import multiprocessing
from env import *
import time

def time_control(period, func):
    run_time = multiprocessing.Process(target=func)
    run_time.start()
    # Wait for 10 seconds or until process finishes
    run_time.join(period)
    # If thread is still active
    if run_time.is_alive():
        # print("running... before changed values...")
        # Terminate - may not work if process is stuck for good
        run_time.terminate()
        # OR Kill - will work for sure, no chance for process to finish nicely however
        # p.kill()
        run_time.join()


class GTW:
    def __init__(self):
        self.mqttclient = MyMQTT()
        self.mqtt_create_state = self.mqttclient.create(USER_NAME, USE_PASSWD)

    def run_modbus(self):
        for i in DEVICE_CSV:
            self.device = get_device_dict(i)  # Получаем словарь из csv девайса
            self.client = TCPClient(self.device['ip_address'][0], self.device['tcp_port'][0])

            if self.device:
                if self.client.connection():
                    self.reading_data = self.client.reader(self.device)
                    idx = -1
                    for i in range(len(self.reading_data['register_address'])):
                        idx+=1
                        print(f"READ-data: register: {self.reading_data ['register_address'][idx]}  value: {self.reading_data ['present_value'][idx]}")

        self.client.disconnect()

    def sent_data(self):
        sent_data = dict.fromkeys(self.reading_data['signal_name'])
        idx = -1
        for i in sent_data:
            idx += 1
            sent_data[i] = self.reading_data['present_value'][idx]
        if self.mqttclient.connect(BROKER, BROKER_PORT):
            self.mqttclient.send(f'{TOPIC}/{self.device["topic"][1]}', sent_data)


gte = GTW()
while True:
    try:
        gte.run_modbus()
        gte.sent_data()
        time.sleep(3)
    except Exception as e:
        logger.exception(e)

import paho.mqtt.client as mqclient
import json
from loguru import logger


class MyMQTT:

    def create(self, user_name, user_passwd):
        try:
            self.client = mqclient.Client(userdata=None, protocol=mqclient.MQTTv311, transport="websockets")
            self.client.ws_set_options(path="/ws", headers=None)
            self.client.username_pw_set(username=user_name, password=user_passwd)
            logger.debug("READY create mqtt-client")
            return True
        except Exception as e:
            logger.exception("FAIL create mqtt-client", e)
            return False

    def connect(self, broker, port):
        try:
            self.client.connect(broker, port=port, keepalive=60, bind_address="")
            logger.debug("READY connect mqtt-client to broker")
            return True
        except Exception as e:
            logger.exception("FAIL connect mqtt-client to broker", e)
            return False

    def send(self, topic, send_data):
        try:
            send_json = json.dumps(send_data)
            self.client.publish(topic, payload=send_json, qos=0, retain=False)
            logger.debug(f"Sending data {send_json}....")
            logger.debug(f"SUCCESSFUL sent data {topic}")
        except Exception as e:
            logger.exception("FAIL sent data to mqtt\n", e)
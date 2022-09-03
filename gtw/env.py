# Список csv-файлов с конфигурациями объектов девайсов, вписанные девайсы будут опрашиваться
DEVICE_LIST = ['device_105_160.csv','device_mod_sim.csv']

#  Чтение группами, если MULTI_READ > 1, по одному, если MULTI_READ=1
MULTI_READ = 20# Так же задает максимальную длину запроса (default=20)

# MQTT параметры
USER_NAME = 'user'
USE_PASSWD = 'user'
BROKER = "mq.demo.promuc.ru"
BROKER_PORT = 15675
TOPIC = "lucenko-mb-gtw"

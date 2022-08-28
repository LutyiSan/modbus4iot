# Список csv-файлов с конфигурациями объектов девайсов, вписанные девайсы будут опрашиваться
DEVICE_LIST = ['device2.csv', 'device.csv']

#  Ограничение на время чтения регистров в секундах
READ_TIMEOUT = 30

#  Чтение группами, если MULTI_READ < 1, по одному, если MULTI_READ=1
MULTI_READ = 20  # Так же задает максимальную длину запроса (default=20)

# MQTT параметры
USER_NAME = 'user'
USE_PASSWD = 'user'
BROKER = "mq.demo.promuc.ru"
BROKER_PORT = 15675
TOPIC = "lucenko-mb-gtw"

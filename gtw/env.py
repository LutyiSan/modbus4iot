# Список csv-файлов с конфигурациями объектов девайсов, вписанные девайсы будут опрашиваться
DEVICE_LIST = ['umg.csv', 'umg2.csv']

#  Чтение группами, если MULTI_READ > 1, по одному, если MULTI_READ=1
MULTI_READ = 124  # Так же задает максимальную длину запроса (default=20)

# MQTT параметры
USER_NAME = 'user'
USE_PASSWD = 'user'
BROKER = "mq.brocker.com"
BROKER_PORT = 15675
TOPIC = "mb4iot"

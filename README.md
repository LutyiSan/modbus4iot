# modbus4iot v.2.1
Данная программа является шлюзом ModbusTCP - MQTT.
# Установка
1. Выполнить команду "sudo git lone https://github.com/LutyiSan/modbus4iot"
2. Перейти в папку "modbus4iot"
3. Заполнить параметры в файле "modbus4iot/gtw/env.py"
4. В папке "modbus4iot/gtw/devices" разместить файлы с конфигурациями девайсов в формате csv( Пример: device.csv).

# Запуск без Docker
1. Находясь в папке modbus4iot, выполнить команду "sudo sh build.sh". !! Только при первом запуске !!
2. Находясь в папке modbus4iot, выполнить команду "sudo sh start.sh"

# Запуск с Docker
1. Находясь в папке modbus4iot, выполнить команду "sudo docker-compose up".

from loguru import logger

reg_types = ['co', 'di', 'hr', 'ir']

data_types = ['uint16', 'int16', 'float16',
              'uint32', 'int32', 'float32',
              'uint64', 'int64', 'float64', 'bool', 'bit']


class Validator:
    state = []

    def check_csv_data(self, check_data):
        self.check_ip(check_data['device_ip'][0])
        self.check_port(check_data['port'][0])
        self.check_reg_type(check_data['reg_type'])
        self.check_reg_address(check_data['reg_address'])
        self.check_quantity(check_data['quantity'])
        self.check_bit(check_data['bit_number'])
        self.check_value_type(check_data['value_type'])
        self.check_scale(check_data['scale'])
        self.check_name(check_data['name'])
        self.check_topic(check_data['topic'][0])
        if False in self.state:
            return False
        else:
            return True

    def check_ip(self, check_data):
        if Validator.validate_ip(check_data):
            self.state.append(True)
        else:
            logger.error("column 'device_ip' must be like  10.21.102.47")
            self.state.append(False)

    def check_port(self, check_data):
        if Validator.validate_digit(check_data, 1, 65535):
            self.state.append(True)
        else:
            logger.error("column 'port' must be a digit 1-65535")
            self.state.append(False)

    def check_reg_type(self, check_data):
        for rt in check_data:
            if Validator.validate_in_enum(reg_types, rt):
                self.state.append(True)
            else:
                logger.error(f"Column 'reg_type' must be a {reg_types}")
                self.state.append(False)

    def check_reg_address(self, check_data):
        for ra in check_data:
            if Validator.validate_digit(ra, 0, 65535):
                self.state.append(True)
            else:
                logger.error("column 'reg_address' must be a digit 0-65535")
                self.state.append(False)

    def check_quantity(self, check_data):
        for qu in check_data:
            if Validator.validate_digit(qu, 1, 4):
                self.state.append(True)
            else:
                logger.error("column 'quantity' must be a digit 1-4")
                self.state.append(False)

    def check_bit(self, check_data):
        for bit in check_data:
            if bit is None:
                self.state.append(True)
            else:
                if Validator.validate_digit(bit, 0, 15):
                    self.state.append(True)
                else:
                    logger.error("column 'bit_number' must be a digit 0-15")
                    self.state.append(False)

    def check_value_type(self, check_data):
        for vt in check_data:
            if Validator.validate_in_enum(data_types, vt):
                self.state.append(True)
            else:
                logger.error(f"column 'value type' must be a {data_types}")
                self.state.append(False)

    def check_scale(self, check_data):
        for scl in check_data:
            try:
                scl = float(scl)
                if Validator.validate_digit(scl, 0.000001, 1000000):
                    self.state.append(True)
                else:
                    logger.error("column 'scale' must be a digit 0.000001-1000000")
                    self.state.append(False)
            except Exception as e:
                logger.error("column 'scale' must be a digit 0.000001-1000000", e)
                self.state.append(False)

    def check_name(self, check_data):
        for nm in check_data:
            if isinstance(nm, str):
                self.state.append(True)
            else:
                logger.error("column 'name' must be a string")
                self.state.append(False)

    def check_topic(self, check_data):
        if isinstance(check_data, str):
            self.state.append(True)
        else:
            logger.error("column 'topic' must be a string")
            self.state.append(False)

    @staticmethod
    def validate_ip(ip):
        a = ip.split('.')
        if len(a) != 4:
            return False
        for x in a:
            if not x.isdigit():
                return False
            i = int(x)
            if i < 0 or i > 255:
                return False
        return True

    @staticmethod
    def validate_digit(value, start, stop):
        if isinstance(value, (int, float)):
            if start <= value <= stop:
                return True
            else:
                return False
        else:
            return False

    @staticmethod
    def validate_in_enum(enum, input_data):
        if input_data in enum:
            return True
        else:
            return False

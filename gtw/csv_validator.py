from loguru import logger


def validate_ip(ipa):
    a = ipa.split('.')
    if len(a) != 4:
        return False
    for x in a:
        if not x.isdigit():
            return False
        i = int(x)
        if i < 0 or i > 255:
            return False
    return True


def validate_digit(value, start, stop):
    if isinstance(value, int):
        if start <= value <= stop:
            return True
        else:
            return False
    else:
        return False


def validate_in_enum(enum, input_data):
    if input_data in enum:
        return True
    else:
        return False


def check_csv_data(check_data):
    state = []
    if validate_ip(check_data['device_ip'][0]):
        state.append(True)
    else:
        logger.error("column 'device_ip' must be like  10.21.102.47")
        state.append(False)
    if validate_digit(check_data['port'][0], 1, 65535):
        state.append(True)
    else:
        logger.error("column 'port' must be a digit 0-65535")
        state.append(False)
    for rt in check_data['reg_type']:
        if validate_in_enum(['hr', 'ir', 'co', 'di'], rt):
            state.append(True)
        else:
            logger.error("column 'reg_type' must be a 'hr', 'ir', 'co', 'di'")
            state.append(False)
    for ra in check_data['reg_address']:
        if validate_digit(ra, 1, 65535):
            state.append(True)
        else:
            logger.error("column 'reg_address' must be a digit 0-65535")
            state.append(False)
    for qu in check_data['quantity']:
        if validate_digit(qu, 1, 4):
            state.append(True)
        else:
            logger.error("column 'quantity' must be a digit 0-4")
            state.append(False)
    for bit in check_data['bit_number']:

        if bit == 'None':

            state.append(True)
        else:

            if validate_in_enum([0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15], bit):
                state.append(True)
            else:
                logger.error("column 'bit_number' must be a digit 0-15")
                state.append(False)
    for vt in check_data['value_type']:
        if validate_in_enum(['uint16', 'int16', 'uint32', 'int32','float', 'bool'], vt):
            state.append(True)
        else:
            logger.error("column 'value type' must be a 'uint16', 'int16', 'uint32', 'int32','float', 'bool'")
            state.append(False)
   # for scl in check_data['scale']:
    #    try:
     #       scl = float(scl)
      #      if validate_digit(scl, 0.000001, 1000000):
       #         state.append(True)
        #    else:
         #       logger.error("column 'scale' must be a digit 0.000001-1000000")
          #      state.append(False)
        #except:
         #   raise ValueError

    for nm in check_data['name']:
        if isinstance(nm, str):
            state.append(True)
        else:
            logger.error("column 'name' must be a string")
            state.append(False)
    for tp in check_data['topic']:
        if isinstance(tp, str):
            state.append(True)
        else:
            logger.error("column 'topic' must be a string")
            state.append(False)

    if False in state:
        return False
    else:
        return True

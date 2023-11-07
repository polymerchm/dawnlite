def string_or_numeric(value):
    try:
        int_value = int(value)
        return int_value
    except:
        try:
            float_value = float(value)
            return float_value
        except:
            return value
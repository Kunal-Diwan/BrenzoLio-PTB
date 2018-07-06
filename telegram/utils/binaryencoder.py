ZERO_CHAR1 = u"\u200C"  # ZERO-WIDTH-NON-JOINER
ZERO_CHAR2 = u"\u200B"  # ZERO-WIDTH-SPACE
ZERO_CHAR3 = u"\u200D"  # ZERO-WIDTH-SPACE


def obfuscate_id_binary(id_):
    binary = "{0:b}".format(id_)
    return binary.replace('0', ZERO_CHAR1).replace('1', ZERO_CHAR2)


def resolve_obfuscated_id(encoded):
    binary = encoded.replace(ZERO_CHAR1, '0').replace(ZERO_CHAR2, '1').replace(ZERO_CHAR3, '')
    try:
        return int(binary, 2)  # convert to decimal
    except ValueError:
        return binary

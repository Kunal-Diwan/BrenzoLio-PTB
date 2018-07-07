import re

ZERO_CHAR_0 = u"\u200C"  # ZERO-WIDTH-NON-JOINER
ZERO_CHAR_1 = u"\u200B"  # ZERO-WIDTH-SPACE
ZERO_CHAR_DENOMINATOR = u"\u200D"  # ZERO-WIDTH-SPACE


def _obfuscate_id_binary(id_):
    binary = "{0:b}".format(int(id_))
    return binary.replace('0', ZERO_CHAR_0).replace('1', ZERO_CHAR_1)


def _resolve_obfuscated_id(encoded):
    binary = encoded.replace(ZERO_CHAR_0, '0').replace(ZERO_CHAR_1, '1').replace(ZERO_CHAR_DENOMINATOR, '')
    try:
        return int(binary, 2)  # convert to decimal
    except ValueError:
        return binary


def insert_callback_id(query, callback_id):
    return ZERO_CHAR_DENOMINATOR + _obfuscate_id_binary(callback_id) + query


def strip_obfuscation(obfuscated):
    return obfuscated.lstrip([ZERO_CHAR_0, ZERO_CHAR_1, ZERO_CHAR_DENOMINATOR])


def callback_id_from_query(text):
    match = re.match(r'^{}([{}{}]+).+?$'.format(
        ZERO_CHAR_DENOMINATOR, ZERO_CHAR_0, ZERO_CHAR_1
    ), text)

    if not match:
        return None

    callback_id = match.group(1)
    return _resolve_obfuscated_id(callback_id)

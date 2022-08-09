from datetime import datetime

COLOURS = {
    "0": 30,
    "1": 34,
    "2": 32,
    "3": 36,
    "4": 31,
    "5": 35,
    "6": 33,
    "7": 37,
    "8": 90,
    "9": 94,
    "a": 92,
    "b": 96,
    "c": 91,
    "d": 95,
    "e": 93,
    "f": 97,
    "r": 0,
    "l": 1,
    "o": 3,
    "n": 4,
    "m": 9,
}


def _print(prefix, tag, msg):
    output = "&r[{}&r][&8{}&r][&7{}&r]&r {}&r".format(prefix, datetime.now().strftime("%d/%m %H:%M:%S.%f"), tag, msg)
    formatted = []
    i = 0
    while i < len(output):
        if i + 1 < len(output) and output[i] == "&" and (
                i - 1 <= 0 or output[i - 1] != "\\" and output[i + 1] in COLOURS):
            formatted.extend(list("\033[{}m".format(COLOURS[output[i + 1]])))
            i += 1
        else:
            formatted.extend(output[i])
        i += 1
    print("".join(formatted))


def log(tag, msg):
    _print("&a+", tag, msg)


def error(tag, msg):
    _print("&c!", tag, "&c" + msg)


def debug(tag, msg):
    _print("&8#", tag, msg)

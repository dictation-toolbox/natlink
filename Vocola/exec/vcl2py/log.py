def set_log(target):
    global LOG
    LOG = target


def print_log(message, no_newline=False):
    global LOG
    if no_newline:
        print(message, file=LOG)
    else:
        print(message, file=LOG)

def close_log():
    global LOG
    LOG.close()

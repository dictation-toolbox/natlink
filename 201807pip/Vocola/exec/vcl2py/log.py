def set_log(target):
    global LOG
    LOG = target


def print_log(message, no_newline=False):
    global LOG
    if no_newline:
        print >>LOG, message,
    else:
        print >>LOG, message

def close_log():
    global LOG
    LOG.close()

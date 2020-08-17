from natlink.loader import *


class MockLoggingHandler(logging.Handler):
    """Mock logging handler to check for expected logs."""

    def __init__(self, *args, **kwargs):
        self.messages: Dict[str, List[str]] = {}
        self.reset()
        logging.Handler.__init__(self, *args, **kwargs)

    def emit(self, record):
        self.messages[record.levelname.lower()].append(record.getMessage())

    def reset(self):
        self.messages = {
            'debug': [],
            'info': [],
            'warning': [],
            'error': [],
            'critical': [],
        }


def test_empty_config_loader():
    logger = logging.getLogger('natlink')
    config = NatlinkConfig([], LogLevel.NOTSET, True, False, True)
    main = NatlinkMain(logger, config)
    log_handler = MockLoggingHandler()
    logger.addHandler(log_handler)
    assert main.module_names == []
    main.load_or_reload_modules(main.module_names)
    assert main.loaded_modules == {}
    assert main.bad_modules == set()
    assert main.load_attempt_times == {}

import pytest

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


@pytest.fixture()
def empty_config():
    config = NatlinkConfig([], LogLevel.DEBUG, True, False, True)
    return config


@pytest.fixture()
def logger():
    logger = logging.Logger('natlink')
    logger.setLevel(logging.DEBUG)
    log_handler = MockLoggingHandler()
    logger.addHandler(log_handler)
    logger.messages = log_handler.messages
    logger.reset = lambda: log_handler.reset()
    return logger


def del_loaded_modules(natlink_main: NatlinkMain):
    for name, mod in natlink_main.loaded_modules.items():
        if name in sys.modules:
            del sys.modules[name]
        if mod:
            del mod


def test_empty_config_loader(empty_config, logger):
    main = NatlinkMain(logger, empty_config)
    assert main.module_names == []
    main.load_or_reload_modules(main.module_names)
    assert main.loaded_modules == {}
    assert main.bad_modules == set()
    assert main.load_attempt_times == {}


def test_load_single_good_script(tmpdir, empty_config, logger, monkeypatch):
    config = empty_config
    config.directories = [tmpdir.strpath]
    a_script = tmpdir.join('_a.py')
    mtime = 123456.0
    a_script.write("""x=0""")
    a_script.setmtime(mtime)
    monkeypatch.setattr(time, 'time', lambda: mtime)

    main = NatlinkMain(logger, config)

    # use instead of add_dirs_to_path
    monkeypatch.syspath_prepend(tmpdir.strpath)
    assert main.module_names == ['_a']

    main.load_or_reload_modules(main.module_names)
    assert set(main.loaded_modules.keys()) == {'_a'}
    assert main.bad_modules == set()
    assert set(main.load_attempt_times.keys()) == {'_a'}
    assert main.load_attempt_times['_a'] == mtime
    assert main.loaded_modules['_a'].x == 0

    del_loaded_modules(main)


def test_reload_single_changed_good_script(tmpdir, empty_config, logger, monkeypatch):
    config = empty_config
    config.directories = [tmpdir.strpath]
    a_script = tmpdir.join('_a.py')
    mtime = 123456.0
    a_script.write("""x=0""")
    a_script.setmtime(mtime)
    monkeypatch.setattr(time, 'time', lambda: mtime)

    main = NatlinkMain(logger, config)

    # use instead of add_dirs_to_path
    monkeypatch.syspath_prepend(tmpdir.strpath)

    main.load_or_reload_modules(main.module_names)

    mtime += 1.0
    a_script.write("""x=1""")
    a_script.setmtime(mtime)

    main.load_or_reload_modules(main.module_names)
    assert set(main.loaded_modules.keys()) == {'_a'}
    assert main.bad_modules == set()
    assert set(main.load_attempt_times.keys()) == {'_a'}
    assert main.load_attempt_times['_a'] == mtime
    assert main.loaded_modules['_a'].x == 1

    del_loaded_modules(main)


def test_reload_should_skip_single_good_unchanged_script(tmpdir, empty_config, logger, monkeypatch):
    config = empty_config
    config.directories = [tmpdir.strpath]
    a_script = tmpdir.join('_a.py')
    mtime = 123456.0
    a_script.write("""x=0""")
    a_script.setmtime(mtime)
    monkeypatch.setattr(time, 'time', lambda: mtime)

    main = NatlinkMain(logger, config)

    # use instead of add_dirs_to_path
    monkeypatch.syspath_prepend(tmpdir.strpath)

    main.load_or_reload_modules(main.module_names)

    a_script.write("""x=1""")
    # set the mtime to the old mtime, so natlink should NOT reload
    a_script.setmtime(mtime)
    mtime += 1.0

    main.load_or_reload_modules(main.module_names)
    assert set(main.loaded_modules.keys()) == {'_a'}
    assert main.bad_modules == set()
    assert set(main.load_attempt_times.keys()) == {'_a'}
    assert main.load_attempt_times['_a'] == mtime

    # make sure it still has the old value, not the new one
    assert main.loaded_modules['_a'].x == 0

    msg = f'skipping unchanged loaded module: _a'
    assert msg in logger.messages['debug']

    del_loaded_modules(main)


def test_load_single_bad_script(tmpdir, empty_config, logger, monkeypatch):
    config = empty_config
    config.directories = [tmpdir.strpath]
    a_script = tmpdir.join('_a.py')
    mtime = 123456.0
    a_script.write("""x=; #a syntax error.""")
    a_script.setmtime(mtime)
    monkeypatch.setattr(time, 'time', lambda: mtime)

    main = NatlinkMain(logger, config)

    # use instead of add_dirs_to_path
    monkeypatch.syspath_prepend(tmpdir.strpath)

    main.load_or_reload_modules(main.module_names)
    assert main.loaded_modules == {}
    assert '_a' not in sys.modules
    assert main.bad_modules == {'_a'}
    assert set(main.load_attempt_times.keys()) == {'_a'}
    assert main.load_attempt_times['_a'] == mtime
    assert len(logger.messages['error']) == 1

    del_loaded_modules(main)


def test_reload_single_changed_bad_script(tmpdir, empty_config, logger, monkeypatch):
    config = empty_config
    config.directories = [tmpdir.strpath]
    a_script = tmpdir.join('_a.py')
    mtime = 123456.0
    a_script.write("""x=; #a syntax error.""")
    a_script.setmtime(mtime)
    monkeypatch.setattr(time, 'time', lambda: mtime)

    main = NatlinkMain(logger, config)

    # use instead of add_dirs_to_path
    monkeypatch.syspath_prepend(tmpdir.strpath)

    main.load_or_reload_modules(main.module_names)
    mtime += 1.0
    a_script.setmtime(mtime)

    logger.reset()
    main.load_or_reload_modules(main.module_names)
    assert main.loaded_modules == {}
    assert '_a' not in sys.modules
    assert main.bad_modules == {'_a'}
    assert set(main.load_attempt_times.keys()) == {'_a'}
    assert main.load_attempt_times['_a'] == mtime
    assert len(logger.messages['error']) == 1

    del_loaded_modules(main)


def test_reload_should_skip_single_bad_unchanged_script(tmpdir, empty_config, logger, monkeypatch):
    config = empty_config
    config.directories = [tmpdir.strpath]
    a_script = tmpdir.join('_a.py')
    mtime = 123456.0
    a_script.write("""x=; #a syntax error.""")
    a_script.setmtime(mtime)
    monkeypatch.setattr(time, 'time', lambda: mtime)

    main = NatlinkMain(logger, config)

    # use instead of add_dirs_to_path
    monkeypatch.syspath_prepend(tmpdir.strpath)

    main.load_or_reload_modules(main.module_names)

    a_script.write("""x=1""")
    # set the mtime to the old mtime, so natlink should NOT reload
    a_script.setmtime(mtime)
    mtime += 1.0

    main.load_or_reload_modules(main.module_names)
    assert main.loaded_modules == {}
    assert '_a' not in sys.modules
    assert main.bad_modules == {'_a'}
    assert set(main.load_attempt_times.keys()) == {'_a'}
    assert main.load_attempt_times['_a'] == mtime

    msg = f'skipping unchanged bad module: _a'
    assert msg in logger.messages['info']

    del_loaded_modules(main)


def test_load_single_good_script_that_was_previously_bad(tmpdir, empty_config, logger, monkeypatch):
    config = empty_config
    config.directories = [tmpdir.strpath]
    a_script = tmpdir.join('_a.py')
    mtime = 123456.0
    a_script.write("""x=; #a syntax error.""")
    a_script.setmtime(mtime)
    monkeypatch.setattr(time, 'time', lambda: mtime)

    main = NatlinkMain(logger, config)

    # use instead of add_dirs_to_path
    monkeypatch.syspath_prepend(tmpdir.strpath)

    main.load_or_reload_modules(main.module_names)
    mtime += 1.0
    a_script.write("""x=1""")
    a_script.setmtime(mtime)

    main.load_or_reload_modules(main.module_names)
    assert set(main.loaded_modules.keys()) == {'_a'}
    assert main.bad_modules == set()
    assert set(main.load_attempt_times.keys()) == {'_a'}
    assert main.load_attempt_times['_a'] == mtime
    assert main.loaded_modules['_a'].x == 1

    del_loaded_modules(main)


def test_load_single_bad_script_that_was_previously_good(tmpdir, empty_config, logger, monkeypatch):
    config = empty_config
    config.directories = [tmpdir.strpath]
    a_script = tmpdir.join('_a.py')
    mtime = 123456.0
    a_script.write("""x=0""")
    a_script.setmtime(mtime)
    monkeypatch.setattr(time, 'time', lambda: mtime)

    main = NatlinkMain(logger, config)

    # use instead of add_dirs_to_path
    monkeypatch.syspath_prepend(tmpdir.strpath)

    main.load_or_reload_modules(main.module_names)
    mtime += 1.0
    a_script.write("""x=; #a syntax error.""")
    a_script.setmtime(mtime)

    main.load_or_reload_modules(main.module_names)
    assert main.loaded_modules == {}
    assert '_a' not in sys.modules
    assert main.bad_modules == {'_a'}
    assert set(main.load_attempt_times.keys()) == {'_a'}
    assert main.load_attempt_times['_a'] == mtime
    assert len(logger.messages['error']) == 1

    del_loaded_modules(main)

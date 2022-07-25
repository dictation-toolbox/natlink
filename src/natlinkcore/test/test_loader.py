
#pylint:disable= C0114, C0116, W0401, W0614, W0621, W0108. W0212

import pytest

from natlinkcore.loader import *

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
    config = NatlinkConfig.get_default_config()
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
    for _name, mod in natlink_main.loaded_modules.items():
        if mod:
            del mod



def test_empty_config_loader(empty_config, logger):
    main = NatlinkMain(logger, empty_config)
    assert main.module_paths_for_user == []
    main.load_or_reload_modules(main.module_paths_for_user)
    assert main.loaded_modules == {}
    assert main.bad_modules == set()
    assert main.load_attempt_times == {}

def test_pre_and_post_load_setter(empty_config, logger):
    main = NatlinkMain(logger, empty_config)
    main.config = empty_config
    with pytest.raises(TypeError):
        main.set_pre_load_callback(None)
    with pytest.raises(TypeError):
        main.set_post_load_callback(None)
    with pytest.raises(TypeError):
        main.set_pre_load_callback("not callable")
    with pytest.raises(TypeError):
        main.set_post_load_callback("not callable")
    cb = lambda: None
    main.set_pre_load_callback(cb)
    main.set_post_load_callback(cb)
    

def test_trigger_load_calls_pre_and_post_load(empty_config, logger, monkeypatch):
    main = NatlinkMain(logger, empty_config)
    main.config = empty_config
    actual = []

    def pre():
        actual.append(1)

    def load(*_args, **_kwargs):
        actual.append(2)

    def post():
        actual.append(3)

    main.set_pre_load_callback(pre)
    main.set_post_load_callback(post)
    monkeypatch.setattr(main, 'load_or_reload_modules', load)

    # this one fails, because now per directory grammars are loaded,
    # line 347 is now commented in favour of lin 351 loader.py (QH)

    main.trigger_load()

    expected = [1, 2, 3]
    assert actual == expected


def test_load_single_good_script(tmpdir, empty_config, logger, monkeypatch):
    config = empty_config
    config.directories_by_user[''] = [tmpdir.strpath]
    a_script = tmpdir.join('_a.py')
    a_path = Path(a_script.strpath)
    mtime = 123456.0
    a_script.write("""x=0""")
    a_script.setmtime(mtime)
    monkeypatch.setattr(time, 'time', lambda: mtime)
    
    main = NatlinkMain(logger, config)
    main.config = config
    assert main.module_paths_for_user == [a_path]

    main.load_or_reload_modules(main.module_paths_for_user)
    assert set(main.loaded_modules.keys()) == {a_path}
    assert '_a' not in sys.modules
    assert main.bad_modules == set()
    assert set(main.load_attempt_times.keys()) == {a_path}
    print('mtime: {mtime}')
    print('main.load_attempt_times[a_path]: {main.load_attempt_times[a_path]}')
    assert main.load_attempt_times[a_path] == mtime
    assert main.loaded_modules[a_path].x == 0

    del_loaded_modules(main)
    

def test_load_single_good_script_from_user_dir(tmpdir, empty_config, logger, monkeypatch):
    config = empty_config
    config.directories_by_user['user'] = [tmpdir.strpath]
    a_script = tmpdir.join('_a.py')
    a_path = Path(a_script.strpath)
    mtime = 123456.0
    a_script.write("""x=0""")
    a_script.setmtime(mtime)
    monkeypatch.setattr(time, 'time', lambda: mtime)

    main = NatlinkMain(logger, config)
    main.config = config
    main.__init__(logger=logger, config=config)

    _modules = main.module_paths_for_user
    assert main.module_paths_for_user == []
    main.user = 'user'   # this way, because now user is a property
    _modules = main.module_paths_for_user
    assert main.module_paths_for_user == [a_path]

    main.load_or_reload_modules(main.module_paths_for_user)
    _mainkeys = set(main.loaded_modules.keys())
    assert set(main.loaded_modules.keys()) == {a_path}
    assert '_a' not in sys.modules
    assert main.bad_modules == set()
    assert set(main.load_attempt_times.keys()) == {a_path}
    assert main.load_attempt_times[a_path] == mtime
    assert main.loaded_modules[a_path].x == 0

    del_loaded_modules(main)
    

def test_reload_single_changed_good_script(tmpdir, empty_config, logger, monkeypatch):
    config = empty_config
    config.directories_by_user[''] = [tmpdir.strpath]
    a_script = tmpdir.join('_a.py')
    a_path = Path(a_script.strpath)
    mtime = 123456.0
    a_script.write("""x=0""")
    a_script.setmtime(mtime)
    monkeypatch.setattr(time, 'time', lambda: mtime)

    main = NatlinkMain(logger, empty_config)
    main.__init__(logger=logger, config=empty_config)
    
    main.load_or_reload_modules(main.module_paths_for_user)

    mtime += 1.0
    a_script.write("""x=1""")
    a_script.setmtime(mtime)
    main.seen.clear()   # is done at start of trigger_load
    main.load_or_reload_modules(main.module_paths_for_user)
    assert set(main.loaded_modules.keys()) == {a_path}
    assert main.bad_modules == set()
    assert set(main.load_attempt_times.keys()) == {a_path}
    assert main.load_attempt_times[a_path] == mtime
    assert main.loaded_modules[a_path].x == 1

    del_loaded_modules(main)
    

def test_remove_single_deleted_good_script(tmpdir, empty_config, logger, monkeypatch):
    config = empty_config
    config.directories_by_user[''] = [tmpdir.strpath]
    a_script = tmpdir.join('_a.py')
    mtime = 123456.0
    a_script.write("""x=0""")
    a_script.setmtime(mtime)
    monkeypatch.setattr(time, 'time', lambda: mtime)

    main = NatlinkMain(logger, config)
    main.config = config

    main.load_or_reload_modules(main.module_paths_for_user)

    a_script.remove()

    main.remove_modules_that_no_longer_exist()
    assert main.loaded_modules == {}
    assert main.bad_modules == set()
    assert main.load_attempt_times == {}

    del_loaded_modules(main)
    

def test_reload_should_skip_single_good_unchanged_script(tmpdir, empty_config, logger, monkeypatch):
    config = empty_config
    main = NatlinkMain(logger, empty_config)
    main.__init__(logger=logger, config=config) 
    config.directories_by_user[''] = [tmpdir.strpath]
    a_script = tmpdir.join('_a.py')
    a_path = Path(a_script.strpath)
    mtime = 123456.0
    a_script.write("""x=0""")
    a_script.setmtime(mtime)
    monkeypatch.setattr(time, 'time', lambda: mtime)

    main.load_or_reload_modules(main.module_paths_for_user)

    a_script.write("""x=1""")
    # set the mtime to the old mtime, so natlink should NOT reload
    a_script.setmtime(mtime)
    mtime += 1.0
    main.seen.clear()   # is done in trigger_load
    main.load_or_reload_modules(main.module_paths_for_user)
    assert set(main.loaded_modules.keys()) == {a_path}
    assert main.bad_modules == set()
    assert set(main.load_attempt_times.keys()) == {a_path}
    assert main.load_attempt_times[a_path] == mtime

    # make sure it still has the old value, not the new one
    assert main.loaded_modules[a_path].x == 0

    ## TODO how solve this (QH)
    msg = 'skipping unchanged loaded module: _a'
    assert msg in logger.messages['debug']

    del_loaded_modules(main)
    

def test_load_single_bad_script(tmpdir, empty_config, logger, monkeypatch):
    config = empty_config
    config.directories_by_user[''] = [tmpdir.strpath]
    a_script = tmpdir.join('_a.py')
    a_path = Path(a_script.strpath)
    mtime = 123456.0
    a_script.write("""x=; #a syntax error.""")
    a_script.setmtime(mtime)
    monkeypatch.setattr(time, 'time', lambda: mtime)

    main = NatlinkMain(logger, config)
    main.__init__(logger=logger, config=config)
    main.load_or_reload_modules(main.module_paths_for_user)
    assert main.loaded_modules == {}
    assert '_a' not in sys.modules
    assert main.bad_modules == {a_path}
    assert set(main.load_attempt_times.keys()) == {a_path}
    assert main.load_attempt_times[a_path] == mtime
    assert len(logger.messages['error']) == 1

    del_loaded_modules(main)
    

def test_remove_single_deleted_bad_script(tmpdir, empty_config, logger, monkeypatch):
    config = empty_config
    config.directories_by_user[''] = [tmpdir.strpath]
    a_script = tmpdir.join('_a.py')
    mtime = 123456.0
    a_script.write(""""x=; #a syntax error.""")
    a_script.setmtime(mtime)
    monkeypatch.setattr(time, 'time', lambda: mtime)

    main = NatlinkMain(logger, config)
    main.__init__(logger=logger, config=config)
    
    main.load_or_reload_modules(main.module_paths_for_user)

    a_script.remove()

    main.remove_modules_that_no_longer_exist()
    assert main.loaded_modules == {}
    assert main.bad_modules == set()
    assert main.load_attempt_times == {}

    del_loaded_modules(main)
    

def test_reload_single_changed_bad_script(tmpdir, empty_config, logger, monkeypatch):
    config = empty_config
    config.directories_by_user[''] = [tmpdir.strpath]
    a_script = tmpdir.join('_a.py')
    a_path = Path(a_script.strpath)
    mtime = 123456.0
    a_script.write("""x=; #a syntax error.""")
    a_script.setmtime(mtime)
    monkeypatch.setattr(time, 'time', lambda: mtime)

    main = NatlinkMain(logger, config)
    main.__init__(logger=logger, config=config)

    main.load_or_reload_modules(main.module_paths_for_user)
    mtime += 1.0
    a_script.setmtime(mtime)

    logger.reset()
    main.seen.clear() 
    main.load_or_reload_modules(main.module_paths_for_user)
    assert main.loaded_modules == {}
    assert '_a' not in sys.modules
    assert main.bad_modules == {a_path}
    assert set(main.load_attempt_times.keys()) == {a_path}
    assert main.load_attempt_times[a_path] == mtime
    assert len(logger.messages['error']) == 1

    del_loaded_modules(main)
    

def test_reload_should_skip_single_bad_unchanged_script(tmpdir, empty_config, logger, monkeypatch):
    config = empty_config
    config.directories_by_user[''] = [tmpdir.strpath]
    a_script = tmpdir.join('_a.py')
    a_path = Path(a_script.strpath)
    mtime = 123456.0
    a_script.write("""x=; #a syntax error.""")
    a_script.setmtime(mtime)
    monkeypatch.setattr(time, 'time', lambda: mtime)

    main = NatlinkMain(logger, config)
    main.__init__(logger=logger, config=config)

    main.load_or_reload_modules(main.module_paths_for_user)

    a_script.write("""x=1""")
    # set the mtime to the old mtime, so natlink should NOT reload
    a_script.setmtime(mtime)
    mtime += 1.0

    main.seen.clear()
    main.load_or_reload_modules(main.module_paths_for_user)
    assert main.loaded_modules == {}
    assert '_a' not in sys.modules
    assert main.bad_modules == {a_path}
    assert set(main.load_attempt_times.keys()) == {a_path}
    assert main.load_attempt_times[a_path] == mtime

    msg = 'skipping unchanged bad module: _a'
    assert msg in logger.messages['info']

    del_loaded_modules(main)
    

def test_load_single_good_script_that_was_previously_bad(tmpdir, empty_config, logger, monkeypatch):
    config = empty_config
    config.directories_by_user[''] = [tmpdir.strpath]
    a_script = tmpdir.join('_a.py')
    a_path = Path(a_script.strpath)
    mtime = 123456.0
    a_script.write("""x=; #a syntax error.""")
    a_script.setmtime(mtime)
    monkeypatch.setattr(time, 'time', lambda: mtime)

    main = NatlinkMain(logger, config)
    main.__init__(logger=logger, config=config)
    main.load_or_reload_modules(main.module_paths_for_user)
    mtime += 1.0
    a_script.write("""x=1""")
    a_script.setmtime(mtime)

    main.seen.clear()
    main.load_or_reload_modules(main.module_paths_for_user)
    assert set(main.loaded_modules.keys()) == {a_path}
    assert main.bad_modules == set()
    assert set(main.load_attempt_times.keys()) == {a_path}
    assert main.load_attempt_times[a_path] == mtime
    assert main.loaded_modules[a_path].x == 1

    del_loaded_modules(main)
    

def test_load_single_bad_script_that_was_previously_good(tmpdir, empty_config, logger, monkeypatch):
    config = empty_config
    config.directories_by_user[''] = [tmpdir.strpath]
    a_script = tmpdir.join('_a.py')
    a_path = Path(a_script.strpath)
    mtime = 123456.0
    a_script.write("""x=0""")
    a_script.setmtime(mtime)
    monkeypatch.setattr(time, 'time', lambda: mtime)

    main = NatlinkMain(logger, config)
    main.__init__(logger=logger, config=config)
    main.__init__(logger=logger, config=config)

    main.load_or_reload_modules(main.module_paths_for_user)
    mtime += 1.0
    a_script.write("""x=; #a syntax error.""")
    a_script.setmtime(mtime)

    main.seen.clear() 
    main.load_or_reload_modules(main.module_paths_for_user)
    assert main.loaded_modules == {}
    assert '_a' not in sys.modules
    assert main.bad_modules == {a_path}
    assert set(main.load_attempt_times.keys()) == {a_path}
    assert main.load_attempt_times[a_path] == mtime
    assert len(logger.messages['error']) == 1

    del_loaded_modules(main)
#     
if __name__ == "__main__":
    pytest.main(['test_loader.py'])

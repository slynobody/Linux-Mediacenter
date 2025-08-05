from contextlib import contextmanager
from collections import defaultdict

from slyguy.log import log
from slyguy.exceptions import Error, Exit


_signals = defaultdict(list)
_skip = defaultdict(int)


ON_ENTRY = 'on_entry'
AFTER_RESET = 'after_reset'
BEFORE_DISPATCH = 'before_dispatch'
AFTER_DISPATCH = 'after_dispatch'
ON_ERROR = 'on_error'
ON_EXCEPTION = 'on_exception'
ON_PLUGIN_EXCEPTION = 'on_plugin_exception'
ON_CLOSE = 'on_close'
ON_DONOR_SET = 'on_donor_set'
ON_DONOR_UNSET = 'on_donor_unset'
ON_EXIT = 'on_exit'


def skip_next(signal):
    _skip[signal] += 1


def on(signal):
    def decorator(f):
        add(signal, f)
        return f
    return decorator


def add(signal, f):
    _signals[signal].append(f)


def emit(signal, *args, **kwargs):
    if _skip[signal] > 0:
        _skip[signal] -= 1
        log.debug("SKIPPED SIGNAL: {}".format(signal))
        return

    log.debug("SIGNAL: {}".format(signal))
    for f in _signals.get(signal, []):
        f(*args, **kwargs)


@contextmanager
def throwable(plugin_caller=False):
    try:
        yield 
    except Exit as e:
        pass
    except Exception as e:
        if plugin_caller:
            emit(ON_PLUGIN_EXCEPTION, e)
        elif isinstance(e, Error):
            emit(ON_ERROR, e)
        else:
            emit(ON_EXCEPTION, e)

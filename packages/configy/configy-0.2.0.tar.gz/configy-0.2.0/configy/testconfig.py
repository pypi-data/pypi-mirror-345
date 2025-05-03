'''
Configy test helper functions
'''
import json
from functools import wraps
from typing import TYPE_CHECKING

from configy.config_container import build_config, config, extend_config

if TYPE_CHECKING:
    from typing import Any, Callable, ParamSpec, TypeVar

    P = ParamSpec('P')
    T = TypeVar('T')


def override_config(data: dict) -> 'Callable[[Callable[P, T]], Callable[P, T]]':
    '''
    Overrides a partial configuration set for the test function/method
    '''
    def wrap(callback: 'Callable[P, T]') -> 'Callable[P, T]':
        @wraps(callback)
        def wrapper(*args: 'P.args', **kwargs: 'P.kwargs') -> 'T':
            old_config = config._get_config()
            new_config = extend_config(
                json.loads(json.dumps(old_config)),
                data,
            )
            config._set_config(new_config)
            try:
                ret = callback(*args, **kwargs)
            except:
                config._set_config(old_config)
                raise
            config._set_config(old_config)
            return ret
        return wrapper
    return wrap


def load_config(**kwconf: 'Any') -> 'Callable[[Callable[P, T]], Callable[P, T]]':
    '''
    Replaces the whole configuration set for the test function/method
    '''
    def wrap(callback: 'Callable[P, T]') -> 'Callable[P, T]':
        @wraps(callback)
        def wrapper(*args: 'P.args', **kwargs: 'P.kwargs') -> 'T':
            old_config = config._get_config()
            case_sensitive = kwconf.get('case_sensitive', True)
            old_case_sensitive = config._case_sensitive
            config._set_config(build_config(**kwconf), case_sensitive)
            try:
                ret = callback(*args, **kwargs)
            except:
                config._set_config(old_config, old_case_sensitive)
                raise
            config._set_config(old_config, old_case_sensitive)
            return ret
        return wrapper
    return wrap

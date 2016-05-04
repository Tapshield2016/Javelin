from functools import wraps

from fabric.api import env
from fabric.context_managers import prefix


def virtualenv(func):
    """Decorator for executing a command inside the project's virtualenv"""
    @wraps(func)
    def wrapper():
        with prefix(env.virtualenvwrapper):
            with prefix("workon %s" % env.virtualenv):
                func()
    return wrapper

import os, re, time
import json
from gai.lib import constants

def get_rc():
    """
    eg. ~/.gairc
    """
    if (not os.path.exists(os.path.expanduser(constants.GAIRC))):
        raise Exception(f"Config file {constants.GAIRC} not found. Please run 'gai init' to initialize the configuration.")
    with open(os.path.expanduser(constants.GAIRC), 'r') as f:
        return json.load(f)


def get_app_path():
    """
    eg. "app_dir" from ~/.gairc
    """
    rc = get_rc()
    app_dir=os.path.abspath(os.path.expanduser(rc["app_dir"]))
    return app_dir

def get_here() -> str:
    """
    Returns the absolute path of the caller script's directory.
    If running in a notebook, returns the current working directory.
    """
    import inspect
    try:
        frame = inspect.stack()[1]
        module = inspect.getmodule(frame[0])
        if module is None or not hasattr(module, "__file__"):
            raise RuntimeError

        caller_file = module.__file__
        caller_dir = os.path.dirname(os.path.abspath(caller_file))
        return caller_dir

    except RuntimeError:
        # ⚠️ Probably running in notebook or interactive shell
        return os.getcwd()
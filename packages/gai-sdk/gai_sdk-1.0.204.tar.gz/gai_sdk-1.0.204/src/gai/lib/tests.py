import os

def get_local_tmp(request=None):

    """
    Construct path for the test file based on the caller's directory.
    """

    if request is None:
        # If request is not provided, use the current working directory
        caller_dir = os.getcwd()   # ✅ current working directory
        tmp_dir = os.path.join(caller_dir, "tmp")
    else:
        caller_file = request.module.__file__   # ✅ test script file
        caller_dir = os.path.dirname(os.path.abspath(caller_file))
        tmp_dir = os.path.join(caller_dir, "tmp", request.node.name)
    return tmp_dir

def make_local_tmp(request=None):

    """
    Create a tmp/ folder using get_local_tmp()
    """

    tmp_dir = get_local_tmp(request)
    os.makedirs(tmp_dir, exist_ok=True)
    return tmp_dir

def get_local_datadir(request=None):

    """
    Create a tmp/ folder inside the directory of the test file that uses this fixture.
    """
    
    if request:
        caller_file = request.module.__file__   # ✅ test script file
        caller_dir = os.path.dirname(os.path.abspath(caller_file))
    else:
        # If request is not provided, use the current working directory
        caller_dir = os.getcwd()

    datadir = os.path.join(caller_dir, "data")

    return datadir
import ctypes
import os
import sys
from threading import Thread


def terminate(thread: Thread) -> None:
    global _lib
    if isinstance(thread, Thread) and thread.is_alive():
        if _lib is None:
            _lib = ctypes.CDLL(_find_lib())
        _lib.main(ctypes.c_longlong(thread._ident))
        try:
            thread._tstate_lock.release()
            thread._stop()
            thread.join(timeout=1)
        except Exception:
            pass


def kill(thread: Thread) -> bool:
    if isinstance(thread, Thread) and thread.is_alive():
        # InterruptedError SystemExit
        _ = ctypes.pythonapi.PyThreadState_SetAsyncExc(ctypes.c_long(thread._ident),
                                                       ctypes.py_object(SystemExit)) == 1
        if _:
            try:
                thread.join(timeout=1)
            except Exception:
                pass
        return _
    return False


def _find_lib():
    paths = [os.path.dirname(__file__),
             os.path.join(os.path.dirname(__file__), "terminate_thread", ),
             os.path.dirname(os.path.abspath(sys.argv[0])),
             os.getcwd(),
             *sys.path,
             ]
    for i in paths:
        p = os.path.join(i, _lib_name)
        if os.path.isfile(p):
            return p
    else:
        raise ModuleNotFoundError(f'Dynamic library "{_lib_name}" not found.')


_lib_name = 'libterminate.dll' if os.name == "nt" else 'libterminate.so'
_lib = None

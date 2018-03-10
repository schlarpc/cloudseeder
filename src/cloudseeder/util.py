try:
    from functools import lru_cache
except ImportError:
    from backports.functools_lru_cache import lru_cache

def get_reason_from_exception(ex):
    """
    Turns an exception into a string similar to the last line of a traceback.
    """
    return '{}: {}'.format(ex.__class__.__name__, str(ex))

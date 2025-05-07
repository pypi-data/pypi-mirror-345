from functools import wraps
import numba


if 1:
    def jit(f):
        if 1:
            return wraps(f)(numba.njit(cache=True)(f))
        else:
            return wraps(f)(f)

    from .putilities import *
    import jDWM.putilities as utilities

else:
    def jit(f):
        return wraps(f)(f)

    from .futilities import *
    import jDWM.futilities as utilities

Ainslie = utilities.Ainslie

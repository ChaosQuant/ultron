# -*- coding: utf-8 -*-

cpdef int pyFinAssert(condition, exception, str msg=*) except -1

cpdef int pyEnsureRaise(exception, str msg=*) except -1

cpdef int pyFinWarning(condition, warn_type, str msg=*)

cpdef bint isClose(double a, double b=*, double rel_tol=*, double abs_tol=*) nogil
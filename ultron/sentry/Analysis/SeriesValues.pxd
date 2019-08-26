# -*- coding: utf-8 -*-

cimport numpy as np

cdef class SeriesValues(object):

    cdef public dict name_mapping
    cdef public np.ndarray values
    cdef public np.ndarray name_array

    cpdef SeriesValues mask(self, np.ndarray flags)
    cpdef list index(self)
    cpdef SeriesValues rank(self, SeriesValues groups=*)
    cpdef SeriesValues top_n(self, int n, SeriesValues groups=*)
    cpdef SeriesValues bottom_n(self, int n, SeriesValues groups=*)
    cpdef SeriesValues top_n_percentile(self, double n, SeriesValues groups=*)
    cpdef SeriesValues bottom_n_percentile(self, double n, SeriesValues groups=*)
    cpdef SeriesValues zscore(self, SeriesValues groups=*)
    cpdef SeriesValues unit(self)

    cpdef SeriesValues mean(self, SeriesValues groups=*)
    cpdef SeriesValues fillna(self, SeriesValues groups=*)
    cpdef SeriesValues percentile(self, SeriesValues groups=*)
    cpdef double dot(self, SeriesValues right)
    cpdef SeriesValues res(self, SeriesValues right)
    cpdef dict to_dict(self)


cdef SeriesValues residue(SeriesValues left, SeriesValues right)
cpdef SeriesValues s_maximum(SeriesValues left, SeriesValues right)
cpdef SeriesValues s_minimum(SeriesValues left, SeriesValues right)

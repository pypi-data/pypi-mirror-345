#!/usr/bin/python

# vim: set expandtab ts=4 sw=4:

__all__ = []


def array_assert(a, b, decimal=None, **kwargs):
    """Function checking whether two arrays are equal in size and almost_equal
    in content (using numpy.testing.assert_almost_equal).

    Parameters
    ----------
    a : ndarray
        First array to check
    b : ndarray
        Second array to check
    decimal : float
        The precisionof the comparison (Default value = None)
    **kwargs : dict
        Extra arguments to pass to numpy.testing.assert_almost_equal

    Returns
    -------

    """
    if decimal is None:
        if a.shape != b.shape:
            raise AssertionError("Sizes of matrices don't match "
                                 "(%s vs %s)" % (str(a.shape),
                                                 str(b.shape)))

        if ((a == b).all()):
            return

        # Otherwise give some info as to why we're asserting
        raise AssertionError("Arrays are not the same:\n"
                             "Array A:%s\nArray B:%s" % (a, b))
    else:
        from numpy.testing import assert_almost_equal
        assert_almost_equal(a, b, decimal, *kwargs)


__all__.append('array_assert')


def ensure_leading_positive(A):
    """This routine ensures that any parameter matrix is of a form which has a
    leading positive identity matrix.  If this is already the case, the
    parameter matrix will be returned unchanged; if it is not, a negated
    version of the parameter matrix will be returned.

    Parameters
    ----------
    A : ndarray
        Parameter matrix (3 or 4D)

    Returns
    -------
    ndarray
        Parameter matrix where the leading identity is guaranteed to be
        positive


    """

    # We just check the first entry in the array
    if A.ndim == 3:
        entry = A[0, 0, 0]
    elif A.ndim == 4:
        entry = A[0, 0, 0, 0]
    else:
        raise ValueError("Parameter matrix must be 3- or 4D")

    # We could add a full check at this point for a leading identity and raise
    # an error if we wanted to
    if entry > 0:
        # We are already positive
        return A

    return -A


__all__.append('ensure_leading_positive')


def ensure_leading_negative(A):
    """This routine ensures that any parameter matrix is of a form which has a
    leading negative identity matrix.  If this is already the case, the
    parameter matrix will be returned unchanged; if it is not, a negated
    version of the parameter matrix will be returned.

    Parameters
    ----------
    A :
        Parameter matrix (3 or 4D)

    Returns
    -------
    ndarray
        Parameter matrix where the leading identity is guaranteed to be
        negative

    """

    # We just check the first entry in the array
    if A.ndim == 3:
        entry = A[0, 0, 0]
    elif A.ndim == 4:
        entry = A[0, 0, 0, 0]
    else:
        raise ValueError("Parameter matrix must be 3- or 4D")

    # We could add a full check at this point for a leading identity and raise
    # an error if we wanted to
    if entry < 0:
        # We are already negative
        return A

    return -A


__all__.append('ensure_leading_negative')

# cython: boundscheck=False, wraparound=False, nonecheck=False
import numpy as np
cimport numpy as np
from libc.math cimport log, exp, atan, sqrt, fabs, copysign

# Define a type alias for double
ctypedef np.float64_t DTYPE_t


cdef double dlga(double dx):
    cdef int i
    cdef double y0, dprec, y
    cdef double[8] dbnum = [-3617.0, 1.0, -691.0, 1.0, -1.0, 1.0, -1.0, 1.0]
    cdef double[8] dbden = [122400.0, 156.0, 360360.0, 1188.0, 1680.0, 1260.0, 360.0, 12.0]
    cdef double dc, dp, dy, dt, ds

    dprec = -log(1.12e-16) / log(10.0)
    dc = 0.5 * log(8.0 * atan(1.0))
    dp = 1.0
    dy = dx
    y = dy
    y0 = exp(0.121189 * dprec + 0.053905)

    while y <= y0:
        dp *= dy
        dy += 1.0
        y = dy

    dt = 1.0 / (dy * dy)
    ds = 43867.0 / 244188.0
    for i in range(8):
        ds = dt * ds + dbnum[i] / dbden[i]

    return (dy - 0.5) * log(dy) - dy + dc + ds / dy - log(dp)


cdef tuple dgamma(double dx):
    cdef double dt
    cdef double dlmach = log(1.7976931348623157e+308)
    dt = dlga(dx)
    if dt >= dlmach:
        return 1.7976931348623157e+308, 2
    return exp(dt), 0


def drecur(int n, int ipoly, double dal, double dbe):
    cdef int iderr = 0
    cdef np.ndarray[DTYPE_t, ndim=1] da = np.zeros(n, dtype=np.float64)
    cdef np.ndarray[DTYPE_t, ndim=1] db = np.zeros(n, dtype=np.float64)
    cdef double dkm1, dalpbe, dt, dal2, dbe2, dlmach = log(1.7976931348623157e+308)
    cdef int k
    cdef double val

    if n < 1:
        return da, db, 3

    if ipoly == 1:
        db[0] = 2.0
        for k in range(1, n):
            dkm1 = float(k)
            db[k] = 1.0 / (4.0 - 1.0 / (dkm1 * dkm1))
        return da, db, iderr

    elif ipoly == 2:
        da[0] = 0.5
        db[0] = 1.0
        for k in range(1, n):
            da[k] = 0.5
            dkm1 = float(k)
            db[k] = 0.25 / (4.0 - 1.0 / (dkm1 * dkm1))
        return da, db, iderr

    elif ipoly == 3:
        db[0] = 4.0 * atan(1.0)
        if n > 1:
            db[1] = 0.5
        for k in range(2, n):
            db[k] = 0.25
        return da, db, iderr

    elif ipoly == 4:
        db[0] = 2.0 * atan(1.0)
        for k in range(1, n):
            db[k] = 0.25
        return da, db, iderr

    elif ipoly == 5:
        db[0] = 4.0 * atan(1.0)
        da[0] = 0.5
        for k in range(1, n):
            db[k] = 0.25
        return da, db, iderr

    elif ipoly == 6:
        if dal <= -1.0 or dbe <= -1.0:
            return da, db, 1
        dalpbe = dal + dbe
        da[0] = (dbe - dal) / (dalpbe + 2.0)
        dt = (dalpbe + 1.0) * log(2.0) + dlga(dal + 1.0) + dlga(dbe + 1.0) - dlga(dalpbe + 2.0)
        if dt > dlmach:
            iderr = 2
            db[0] = 1.7976931348623157e+308
        else:
            db[0] = exp(dt)
        if n == 1:
            return da, db, iderr
        dal2 = dal * dal
        dbe2 = dbe * dbe
        da[1] = (dbe2 - dal2) / ((dalpbe + 2.0) * (dalpbe + 4.0))
        db[1] = 4.0 * (dal + 1.0) * (dbe + 1.0) / ((dalpbe + 3.0) * (dalpbe + 2.0) ** 2)
        for k in range(2, n):
            dkm1 = float(k)
            da[k] = 0.25 * (dbe2 - dal2) / (
                dkm1 * dkm1 * (1.0 + 0.5 * dalpbe / dkm1) * (1.0 + 0.5 * (dalpbe + 2.0) / dkm1)
            )
            db[k] = 0.25 * (1.0 + dal / dkm1) * (1.0 + dbe / dkm1) * (1.0 + dalpbe / dkm1) / (
                (1.0 + 0.5 * (dalpbe + 1.0) / dkm1)
                * (1.0 + 0.5 * (dalpbe - 1.0) / dkm1)
                * (1.0 + 0.5 * dalpbe / dkm1) ** 2
            )
        return da, db, iderr

    elif ipoly == 7:
        if dal <= -1.0:
            return da, db, 1
        da[0] = dal + 1.0
        val, iderr = dgamma(dal + 1.0)
        db[0] = 1.7976931348623157e+308 if iderr == 2 else val
        for k in range(1, n):
            dkm1 = float(k)
            da[k] = 2.0 * dkm1 + dal + 1.0
            db[k] = dkm1 * (dkm1 + dal)
        return da, db, iderr

    elif ipoly == 8:
        db[0] = sqrt(4.0 * atan(1.0))
        for k in range(1, n):
            db[k] = 0.5 * float(k)
        return da, db, iderr

    else:
        return da, db, 4


def dgauss(np.ndarray[DTYPE_t, ndim=1] dalpha,
           np.ndarray[DTYPE_t, ndim=1] dbeta):
    """
    Cython version of the Fortran dgauss subroutine.
    Returns dzero, dweigh, ierr.
    """

    cdef int n = dalpha.shape[0]
    cdef int ierr = 0
    cdef int i, ii, j, k, l, m, mml
    cdef double deps = 1.12e-16
    cdef double dp, dg, dr, ds, dc, df, db

    cdef np.ndarray[DTYPE_t, ndim=1] dzero = np.zeros(n, dtype=np.float64)
    cdef np.ndarray[DTYPE_t, ndim=1] dweigh = np.zeros(n, dtype=np.float64)
    cdef np.ndarray[DTYPE_t, ndim=1] de = np.zeros(n, dtype=np.float64)

    if n < 1:
        return dzero, dweigh, -1

    dzero[0] = dalpha[0]
    if dbeta[0] < 0.0:
        return dzero, dweigh, -2

    dweigh[0] = 1.0
    de[n - 1] = 0.0

    for k in range(1, n):
        dzero[k] = dalpha[k]
        if dbeta[k] < 0.0:
            return dzero, dweigh, -2
        de[k - 1] = sqrt(dbeta[k])
        dweigh[k] = 0.0

    for l in range(n):
        j = 0
        while True:
            for m in range(l, n):
                if m == n - 1:
                    break
                if fabs(de[m]) <= deps * (fabs(dzero[m]) + fabs(dzero[m + 1])):
                    break

            dp = dzero[l]

            if m == l:
                break  # goto 240

            if j == 30:
                return dzero, dweigh, l  # Error condition

            j += 1
            dg = (dzero[l + 1] - dp) / (2.0 * de[l])
            dr = sqrt(dg * dg + 1.0)
            dg = dzero[m] - dp + de[l] / (dg + copysign(dr, dg))

            ds = 1.0
            dc = 1.0
            dp = 0.0
            mml = m - l

            for ii in range(1, mml + 1):
                i = m - ii
                df = ds * de[i]
                db = dc * de[i]

                if fabs(df) < fabs(dg):
                    ds = df / dg
                    dr = sqrt(ds * ds + 1.0)
                    de[i + 1] = dg * dr
                    dc = 1.0 / dr
                    ds = ds * dc
                else:
                    dc = dg / df
                    dr = sqrt(dc * dc + 1.0)
                    de[i + 1] = df * dr
                    ds = 1.0 / dr
                    dc = dc * ds

                dg = dzero[i + 1] - dp
                dr = (dzero[i] - dg) * ds + 2.0 * dc * db
                dp = ds * dr
                dzero[i + 1] = dg + dp
                dg = dc * dr - db

                df = dweigh[i + 1]
                dweigh[i + 1] = ds * dweigh[i] + dc * df
                dweigh[i] = dc * dweigh[i] - ds * df

            dzero[l] -= dp
            de[l] = dg
            de[m] = 0.0

        # Label 240 (continue outer loop)

    # Sorting section
    for ii in range(1, n):
        i = ii - 1
        k = i
        dp = dzero[i]
        for j in range(ii, n):
            if dzero[j] < dp:
                k = j
                dp = dzero[j]
        if k != i:
            dzero[k], dzero[i] = dzero[i], dzero[k]
            dweigh[k], dweigh[i] = dweigh[i], dweigh[k]

    # Final weight update
    for k in range(n):
        dweigh[k] = dbeta[0] * dweigh[k] * dweigh[k]

    return dzero, dweigh, ierr


def dlob(np.ndarray[DTYPE_t, ndim=1] dalpha,
         np.ndarray[DTYPE_t, ndim=1] dbeta,
         double dleft, double dright):
    """
    Computes nodes and weights for the Lobatto quadrature.

    Parameters:
        dalpha (np.ndarray): Main diagonal of Jacobi matrix (length n)
        dbeta  (np.ndarray): Subdiagonal (length n)
        dleft  (float): Left endpoint
        dright (float): Right endpoint

    Returns:
        dzero (np.ndarray): Quadrature nodes (length n+2)
        dweigh (np.ndarray): Quadrature weights (length n+2)
        ierr (int): Error flag
    """

    cdef int n = dalpha.shape[0]
    cdef int np1 = n + 1
    cdef int np2 = n + 2
    cdef int k, ierr

    cdef double dp0l = 0.0, dp0r = 0.0
    cdef double dp1l = 1.0, dp1r = 1.0
    cdef double dpm1l, dpm1r, ddet

    cdef np.ndarray[DTYPE_t, ndim=1] da = np.zeros(np2, dtype=np.float64)
    cdef np.ndarray[DTYPE_t, ndim=1] db = np.zeros(np2, dtype=np.float64)
    cdef np.ndarray[DTYPE_t, ndim=1] dzero = np.zeros(np2, dtype=np.float64)
    cdef np.ndarray[DTYPE_t, ndim=1] dweigh = np.zeros(np2, dtype=np.float64)
    cdef np.ndarray[DTYPE_t, ndim=1] de = np.zeros(np2, dtype=np.float64)

    # Fill in da and db
    for k in range(n):
        da[k] = dalpha[k]
        db[k] = dbeta[k]

    # Compute the boundary recurrence terms
    for k in range(n):
        dpm1l = dp0l
        dp0l = dp1l
        dpm1r = dp0r
        dp0r = dp1r

        dp1l = (dleft - da[k]) * dp0l - db[k] * dpm1l
        dp1r = (dright - da[k]) * dp0r - db[k] * dpm1r

    # Final da and db entries
    ddet = dp1l * dp0r - dp1r * dp0l
    da[np2 - 1] = (dleft * dp1l * dp0r - dright * dp1r * dp0l) / ddet
    db[np2 - 1] = (dright - dleft) * dp1l * dp1r / ddet

    # Call to the Cython version of dgauss
    dzero, dweigh, ierr = dgauss(da, db)

    return dzero, dweigh, ierr


def dradau(np.ndarray[DTYPE_t, ndim=1] dalpha,
           np.ndarray[DTYPE_t, ndim=1] dbeta,
           double dend):
    """
    Radau quadrature generator via modified Jacobi matrix.

    Parameters:
        dalpha (ndarray[n]): Diagonal coefficients of Jacobi matrix.
        dbeta (ndarray[n]): Off-diagonal coefficients.
        dend (float): Endpoint to be included in the Radau rule.

    Returns:
        dzero (ndarray[n+1]): Quadrature nodes.
        dweigh (ndarray[n+1]): Quadrature weights.
        ierr (int): Error flag from dgauss.
    """
    cdef int n = dalpha.shape[0]
    cdef int np1 = n + 1
    cdef int k
    cdef double dp0 = 0.0, dp1 = 1.0, dpm1

    cdef np.ndarray[DTYPE_t, ndim=1] da = np.zeros(np1, dtype=np.float64)
    cdef np.ndarray[DTYPE_t, ndim=1] db = np.zeros(np1, dtype=np.float64)
    cdef np.ndarray[DTYPE_t, ndim=1] dzero = np.zeros(np1, dtype=np.float64)
    cdef np.ndarray[DTYPE_t, ndim=1] dweigh = np.zeros(np1, dtype=np.float64)
    cdef np.ndarray[DTYPE_t, ndim=1] de = np.zeros(np1, dtype=np.float64)
    cdef int ierr = 0

    # Copy dalpha and dbeta into extended arrays
    for k in range(n):
        da[k] = dalpha[k]
        db[k] = dbeta[k]

    # Compute modified diagonal element for Radau rule
    for k in range(n):
        dpm1 = dp0
        dp0 = dp1
        dp1 = (dend - da[k]) * dp0 - db[k] * dpm1

    da[np1 - 1] = dend - db[np1 - 1] * dp0 / dp1

    # Call Gauss quadrature on the modified matrix
    dzero, dweigh, ierr = dgauss(da, db)

    return dzero, dweigh, ierr

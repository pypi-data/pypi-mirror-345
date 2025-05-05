# SPDX-FileCopyrightText: Copyright 2022, Siavash Ameli <sameli@berkeley.edu>
# SPDX-License-Identifier: BSD-3-Clause
# SPDX-FileType: SOURCE
#
# This program is free software: you can redistribute it and/or modify it under
# the terms of the license found in the LICENSE.txt file in the root directory
# of this source tree.


# =======
# Imports
# =======

import numpy
import scipy
from .._definitions.types cimport LongIndexType, FlagType
from .._cy_linear_algebra import matmul, cho_factor, lu_factor
from .._device import InstructionsCounter
from .benchmark cimport Benchmark
import matplotlib.pyplot as plt
import texplot

# To avoid cython's bug that does not recognizes "long double" in template []
ctypedef long double long_double

__all__ = ['get_instructions_per_flop']


# =========================
# get instructions per flop
# =========================

cpdef get_instructions_per_flop(
        task='matmul',
        dtype='float64',
        impl='native',
        min_n=100,
        max_n=500,
        num_n=6,
        plot=False):
    """
    Counts the hardware instructions of computing a single FLOP of a benchmark
    task on the current processor.

    The goal of this function is to be used to measure the computational
    complexity of an algorithm. To measure the complexity, we use floating
    point operations (FLOPs). We define a FLOP by a fused multiply-add
    operation.

    FLOPs cannot be directly measured on the processor. Instead, we measure the
    `hardware instructions` of the processor. To measure the FLOPs of an
    algorithm, we can divide the instructions it takes to run the desired
    algorithm by the instructions it takes to compute a single FLOP of another
    benchmark task the same processor and same compiler configuration. The aim
    of this function is to measure the instructions of a unit FLOP.

    A benchmark task is a basic mathematical operation, such as matrix-matrix
    multiplication, LU factorization, or Cholesky decomposition on a matrix.
    Assuming the matrix size is :math:`n`, the complexity of either of the
    tasks provided in are as follows

    ==============  =============================  =======================
    Code name       Task name                      Complexity
    ==============  =============================  =======================
    ``'matmul'``    matrix-matrix multiplication   :math:`n^3`
    ``'gramian'``   Gramian matrix multiplication  :math:`\\frac{1}{2}n^3`
    ``'cholesky'``  Cholesky decomposition         :math:`\\frac{1}{3}n^3`
    ``'plu'``       PLU decomposition              :math:`\\frac{2}{3}n^3`
    ``'lu'``        LU decomposition               :math:`\\frac{2}{3}n^3`
    ==============  =============================  =======================

    This function measures the instructions of a benchmark task as :math:`n`
    tends to infinity.

    Parameters
    ----------
        task : {'matmul', 'gramian', 'cholesky', 'lu', 'plu'}, default='matmul'
            The benchmark task to count its hardware instructions.

            * ``'matmul'``: matrix-matrix multiplication task.
            * ``'gramian'``: Gramian matrix-matrix multiplication task.
            * ``'cholesky'``: Cholesky decomposition task.
            * ``'lu'``: LU decomposition task.
            * ``'plu'``: PLU decomposition task.

        dtype : {'float32', 'float64', 'float128'}, default='float64'
            The type of the test data.

        impl : {``'detkit'``, ``'lapack'``, ``'blas'``},\
                default:``'native'``
            Implementation to execute the benchmark.

            * ``'native'``: uses native implementation of tasks (on single
              thread).
            * ``'lapack'``: uses LAPACK implementation of tasks using scipy.
            * ``'blas'``: uses BLAS implementation of tasks using numpy.

        min_n : int, default=100
            Minimum square matrix size to be tested.

        max_n : int, default=500
            Maximum square matrix size to be tested.

        num_n : int, default=10
            Number of various matrix sizes to try.

        plot : bool, default=False
            If `True`, the estimation of FLOPs versus various matrix sizes is
            plotted.

    Returns
    -------
        inst : int
            Count of hardware instructions. If the operating system or the
            processor does not support the feature of counting the hardware
            instructions, `-1` is returned.

    See Also
    --------

        check_perf_support
        loggdet
        logpdet
        memdet

    Notes
    -----
        * Instructions count depends on the processor and the compiler
          configurations that compiles the package. Results may vary on
          different computers.

        * Instruction counts, :math:`c`, also varies by the size of the
          matrices used in the benchmark test, but it converges when the matrix
          size, :math:`n` is very large. To obtain a unique number, we use the
          following asymptotic relation:

          .. math::

              c(n) = c_{\\infty} + \\frac{\\alpha}{n}

          To measure :math:`c_{\\infty}`, this function measures :math:`c(n)`
          on several matrix sizes :math:`n` and uses the above relation to find
          their asymptote.

        * It appears that the choice of `dtype` does not have an effect on the
          count of hardware instructions.

    Examples
    --------
    We can measure the FLOPs of computing, for instance, `loggdet` as follows:

    .. code-block:: python

        >>> import numpy
        >>> from detkit import loggdet, get_instructions_per_count

        >>> # Generate a random matrix
        >>> n, m = 1000, 500
        >>> rng = numpy.random.RandomState(0)
        >>> A = rng.rand(n, n)
        >>> X = rng.rand(n, m)

        >>> # Measure the hardware instructions to compute loggdet of matrix
        >>> loggdet_, sign, inst = loggdet(A, X, flops=True)
        >>> print(inst)
        11009228170

        >>> # Measure hardware instructions of a single FLOP
        >>> benchmark_inst = get_instructions_per_flop(task='matmul')
        >>> print(benchmark_int)
        5.21

        >>> # Calculate FLOPs of loggdet function
        >>> flops = int(float(inst) / float(benchmark_inst))
        >>> print(flops)
        2110324959

        >>> # Calculate coefficient of complexity
        >>> print(flops / n**3)
        2.11

    Example of plotting how the instructions are estimated:

    .. code-block:: python

        >>> import detkit
        >>> inst = detkit.get_instructions_per_flop(dtype='float32', min_n=100,
        ...                                         max_n=500, num_n=10,
        ...                                         plot=True)
        >>> # inst is the intercept of the regression line in the plot
        >>> print(inst)
        4.225773707890822

    .. image:: ../_static/images/plots/simd.png
        :align: center
        :class: custom-dark
    """

    n = (1.0 / numpy.linspace(1.0/min_n, 1.0/max_n, num_n) + 0.5).astype(int)
    inst_per_flop = -numpy.ones((n.size, ), dtype=float)

    for i in range(n.size):

        if impl == 'native':
            inst_per_flop[i] = _native_benchmark(task, dtype, n[i])
        elif impl == 'lapack':
            inst_per_flop[i] = _lapack_benchmark(task, dtype, n[i])
        elif impl == 'blas':
            inst_per_flop[i] = _blas_benchmark(task, dtype, n[i])
        else:
            raise ValueError('"impl" is not valid.')

        # Negative means perf is not supported
        if inst_per_flop[i] < 0.0:
            inst_per_flop[i] = numpy.nan

    # This means perf is not supported.
    if numpy.any(numpy.isnan(inst_per_flop)):
        return numpy.nan

    # Find inst_per_flop when n tends to infinity using an exponential model
    # inst_per_flop = a/n + b
    slope, intercept, mask = _quantile_filtered_regression(
            1.0/n, inst_per_flop)

    if plot:
        n_inv = numpy.linspace(0, numpy.max(1.0/n), 100)
        interp = slope * n_inv + intercept

        with texplot.theme():
            fig, ax = plt.subplots(figsize=(6, 4))
            ax.plot(1.0/n[mask], inst_per_flop[mask], 'o', color='black',
                    label='Measurement')
            ax.plot(1.0/n[~mask], inst_per_flop[~mask], 'o', color='white',
                    markeredgecolor='black', label='Outliers')
            ax.plot(n_inv, interp, '--', color='black', label='Regression')
            ax.scatter(n_inv[0], interp[0], s=50, zorder=3, clip_on=False,
                       color='maroon', label=r'Estimate at $n \to \infty$')
            ax.set_xlim([n_inv[0], n_inv[-1]])
            ax.legend(fontsize='small')
            ax.set_xlabel(r'$n^{-1}$')
            ax.set_ylabel(r'Retired Instructions / $n^3$')
            ax.set_title(r'Estimating Instructions per FLOP at $n \to \infty$')

            texplot.show_or_save_plot(plt, default_filename='simd',
                                      transparent_background=True, dpi=200,
                                      show_and_save=False, verbose=True)

    # In the limit n=infinity, b is the number of inst_per_flop
    inst_per_flop_limit = float(intercept)

    return inst_per_flop_limit


# ============================
# quantile filtered regression
# ============================

def _quantile_filtered_regression(x, y, threshold=1.5, max_iter=10, tol=1e-6):
    """
    Perform iterative least squares regression, removing extreme residuals in
    each iteration.
    
    Parameters
    ----------
    
    x : numpy array (independent variable)
    y : numpy array (dependent variable)
    threshold : float, multiplier for IQR-based outlier detection
    max_iter : int, maximum number of iterations
    tol : float, stopping threshold for change in data size

    Returns
    -------

    slope : float, final slope
    intercept : float, final intercept
    mask : boolean numpy array, True for inliers, False for outliers
    """

    x = numpy.array(x)
    y = numpy.array(y)
    
    # Start with all points as inliers
    mask = numpy.ones_like(y, dtype=bool)

    for _ in range(max_iter):
        # Fit regression to current inliers
        slope, intercept = numpy.polyfit(x[mask], y[mask], deg=1)
        y_pred = slope * x + intercept
        residuals = y - y_pred

        # Compute IQR
        Q1, Q3 = numpy.percentile(residuals[mask], [25, 75])
        IQR = Q3 - Q1
        lower_bound = Q1 - threshold * IQR
        upper_bound = Q3 + threshold * IQR

        # Update mask: Keep only points within IQR range
        new_mask = (residuals >= lower_bound) & (residuals <= upper_bound)

        # Stop if no more changes in mask
        if numpy.sum(mask) - numpy.sum(new_mask) < tol:
            break

        mask = new_mask  # Update mask for next iteration

    return slope, intercept, mask


# ================
# lapack benchmark
# ================

cpdef _lapack_benchmark(task, dtype, n):
    """
    Benchmark using LAPACK implementation.
    """

    A = numpy.random.randn(n, n)
    if task in ['matmul', 'gramian']:
        B = numpy.random.randn(n, n)
        C = numpy.random.randn(n, n)
    elif task == 'cholesky':
        A = A.T @ A

    if dtype == 'float32':
        A = A.astype(numpy.float32)
        if task in ['matmul', 'gramian']:
            B = B.astype(numpy.float32)
            C = B.astype(numpy.float32)

    elif dtype == 'float64':
        A = A.astype(numpy.float64)
        if task in ['matmul', 'gramian']:
            B = B.astype(numpy.float64)
            C = C.astype(numpy.float64)

    else:
        raise ValueError('When "impl" is set to "lapack", "dtype" should ' +
                         'be "float32", "float64".')

    A = numpy.asfortranarray(A)
    if task in ['matmul', 'gramian']:
        B = numpy.asfortranarray(B)
        C = numpy.asfortranarray(C)

    # Start counting
    ic = InstructionsCounter()
    ic.start()

    # Perform task
    if task in ['matmul', 'gramian']:
        matmul(A, B, C)
    elif task == 'cholesky':
        cho_factor(A)
    elif task in ['lu', 'plu']:
        lu_factor(A)
    else:
        raise ValueError('"task" is not recognized.')

    # Stop counting
    ic.stop()
    inst = ic.get_count()

    # Negative means the perf_tool is not installed on Linux OS.
    if inst < 0:
        return numpy.nan

    # Flops for matrix-matrix multiplication
    benchmark_flops = n**3
    if task in ['matmul', 'gramian']:
        pass
    elif task == 'cholesky':
        benchmark_flops *= 1.0/3.0
    elif task in ['lu', 'plu']:
        benchmark_flops *= 2.0/3.0
    else:
        raise ValueError('"task" is not recognized.')

    inst_per_flop = inst / benchmark_flops

    return inst_per_flop


# ==============
# blas benchmark
# ==============

cpdef _blas_benchmark(task, dtype, n):
    """
    Benchmark using BLAS implementation.
    """

    A = numpy.random.randn(n, n)
    if task in ['matmul', 'gramian']:
        B = numpy.random.randn(n, n)
        C = numpy.random.randn(n, n)
    elif task == 'cholesky':
        A = A.T @ A

    if dtype == 'float32':
        A = A.astype(numpy.float32)
        if task in ['matmul', 'gramian']:
            B = B.astype(numpy.float32)
            C = B.astype(numpy.float32)

    elif dtype == 'float64':
        A = A.astype(numpy.float64)
        if task in ['matmul', 'gramian']:
            B = B.astype(numpy.float64)
            C = C.astype(numpy.float64)

    else:
        raise ValueError('When "impl" is set to "openblblas", "dtype" ' +
                         'should be "float32", "float64".')

    # Start counting
    ic = InstructionsCounter()
    ic.start()

    # Perform task
    if task in ['matmul', 'gramian']:
        C = A @ B
    elif task == 'cholesky':
        numpy.linalg.cholesky(A)
    elif task in ['lu', 'plu']:
        scipy.linalg.lu(A)
    else:
        raise ValueError('"task" is not recognized.')

    # Stop counting
    ic.stop()
    inst = ic.get_count()

    # Negative means the perf_tool is not installed on Linux OS.
    if inst < 0:
        return numpy.nan

    # Flops for matrix-matrix multiplication
    benchmark_flops = n**3
    if task in ['matmul', 'gramian']:
        pass
    elif task == 'cholesky':
        benchmark_flops *= 1.0/3.0
    elif task in ['lu', 'plu']:
        benchmark_flops *= 2.0/3.0
    else:
        raise ValueError('"task" is not recognized.')

    inst_per_flop = inst / benchmark_flops

    return inst_per_flop


# ================
# native benchmark
# ================

cpdef _native_benchmark(task, dtype, n):
    """
    Benchmark using in-house implementation.
    """

    if dtype == 'float32':
        inst = _get_instructions_float(task, n)
    elif dtype == 'float64':
        inst = _get_instructions_double(task, n)
    elif dtype == 'float128':
        inst = _get_instructions_long_double(task, n)
    else:
        raise ValueError('"dtype" should be "float32", "float64", or ' +
                         '"float128".')

    # Negative means the perf_tool is not installed on Linux OS.
    if inst < 0:
        return numpy.nan

    # Flops for matrix-matrix multiplication
    benchmark_flops = n**3
    if task == 'matmul':
        pass
    elif task == 'gramian':
        benchmark_flops *= 1.0/2.0
    elif task == 'cholesky':
        benchmark_flops *= 1.0/3.0
    elif task == 'lu':
        benchmark_flops *= 2.0/3.0
    elif task == 'plu':
        benchmark_flops *= 2.0/3.0
    else:
        raise ValueError('"task" is not recognized.')

    inst_per_flop = inst / benchmark_flops

    return inst_per_flop


# ======================
# get instructions float
# ======================

cpdef long long _get_instructions_float(
        task,
        int n):
    """
    Specialized for float type.
    """

    # A c-pointer just to specialize the template function to float
    cdef float* dummy_var = NULL
    cdef long long inst = -1

    if task == 'matmul':
        inst = Benchmark[float].matmul(dummy_var, n)
    elif task == 'gramian':
        inst = Benchmark[float].gramian(dummy_var, n)
    elif task == 'cholesky':
        inst = Benchmark[float].cholesky(dummy_var, n)
    elif task == 'lu':
        inst = Benchmark[float].lu(dummy_var, n)
    elif task == 'plu':
        inst = Benchmark[float].plu(dummy_var, n)
    else:
        raise ValueError('"task" is not recognized.')

    return inst


# =======================
# get instructions double
# =======================

cpdef long long _get_instructions_double(
        task,
        int n):
    """
    Specialized for double type.
    """

    # A c-pointer just to specialize the template function to double
    cdef double* dummy_var = NULL
    cdef long long inst = -1

    if task == 'matmul':
        inst = Benchmark[double].matmul(dummy_var, n)
    elif task == 'gramian':
        inst = Benchmark[double].gramian(dummy_var, n)
    elif task == 'cholesky':
        inst = Benchmark[double].cholesky(dummy_var, n)
    elif task == 'lu':
        inst = Benchmark[double].lu(dummy_var, n)
    elif task == 'plu':
        inst = Benchmark[double].plu(dummy_var, n)
    else:
        raise ValueError('"task" is not recognized.')

    return inst


# ============================
# get instructions long double
# ============================

cpdef long long _get_instructions_long_double(
        task,
        int n):
    """
    Specialized for long double type.
    """

    # A c-pointer just to specialize the template function to long double
    cdef long double* dummy_var = NULL
    cdef long long inst = -1

    if task == 'matmul':
        inst = Benchmark[long_double].matmul(dummy_var, n)
    elif task == 'gramian':
        inst = Benchmark[long_double].gramian(dummy_var, n)
    elif task == 'cholesky':
        inst = Benchmark[long_double].cholesky(dummy_var, n)
    elif task == 'lu':
        inst = Benchmark[long_double].lu(dummy_var, n)
    elif task == 'plu':
        inst = Benchmark[long_double].plu(dummy_var, n)
    else:
        raise ValueError('"task" is not recognized.')

    return inst

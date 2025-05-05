.. _api:

=============
API Reference
=============

.. rubric:: Matrix Determinant

Functions for computing determinant and related quantities of matrices.

.. autosummary::
    :toctree: generated
    :caption: Matrix Determinant
    :recursive:
    :template: autosummary/member.rst

    detkit.logdet
    detkit.loggdet
    detkit.logpdet
    detkit.memdet

Classes for fitting and extrapolation of log-determinants.

.. autosummary::
    :toctree: generated
    :caption: Profiling
    :recursive:
    :template: autosummary/class.rst

    detkit.FitLogdet

.. rubric:: Matrix Decompositions

LU, LDL and Cholesky factorizations for sub-matrices, as well as matrix orthogonalizations.

.. autosummary::
    :toctree: generated
    :caption: Supplementary
    :recursive:
    :template: autosummary/member.rst

    detkit.orthogonalize
    detkit.ortho_complement
    detkit.lu_factor
    detkit.ldl_factor
    detkit.cho_factor

.. rubric:: Solving Linear Systems

Solving linear systems for sub-matrices based on LU, LDL and Cholesky decompositions.

.. autosummary::
    :toctree: generated
    :caption: Solving Linear Systems
    :recursive:
    :template: autosummary/member.rst

    detkit.lu_solve
    detkit.ldl_solve
    detkit.cho_solve
    detkit.solve_triangular

.. rubric:: BLAS Operations

BLAS operations for sub-matrices.

.. autosummary::
    :toctree: generated
    :caption: BLAS Operations
    :recursive:
    :template: autosummary/member.rst

    detkit.matmul

.. rubric:: Datasets

Functions to create sample dataset to be used for test and benchmarking purposes.

.. autosummary::
    :toctree: generated
    :caption: Datasets
    :recursive:
    :template: autosummary/member.rst

    detkit.electrocardiogram
    detkit.covariance_matrix
    detkit.design_matrix

.. rubric:: Profiling

Utility classes for profiling memory and process.

.. autosummary::
    :toctree: generated
    :caption: Profiling
    :recursive:
    :template: autosummary/class.rst

    detkit.Memory
    detkit.Disk
    detkit.Profile

.. rubric:: Profiling Utilities

Utility functions for profiling memory and process.
   
.. autosummary::
    :toctree: generated
    :caption: Profiling Utilities
    :recursive:
    :template: autosummary/member.rst

    detkit.get_config
    detkit.check_perf_support
    detkit.get_instructions_per_flop
    detkit.get_processor_name
    detkit.human_readable_time
    detkit.human_readable_mem

Utility classes for profiling process.
   
.. autosummary::
    :toctree: generated
    :caption: Profiling Utilities
    :recursive:
    :template: autosummary/class.rst

    detkit.InstructionsCounter

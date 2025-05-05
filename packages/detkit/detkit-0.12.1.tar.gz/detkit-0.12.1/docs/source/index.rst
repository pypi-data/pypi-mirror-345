|project| Documentation
***********************

|license| |deploy-docs|

A python package to compute common functions involving determinant of matrices used in machine learning.

.. grid:: 4

    .. grid-item-card:: GitHub
        :link: https://github.com/ameli/detkit
        :text-align: center
        :class-card: custom-card-link

    .. grid-item-card:: PyPI
        :link: https://pypi.org/project/detkit/
        :text-align: center
        :class-card: custom-card-link

    .. grid-item-card:: Anaconda Cloud
        :link: https://anaconda.org/s-ameli/detkit
        :text-align: center
        :class-card: custom-card-link

    .. grid-item-card:: Docker Hub
        :link: https://hub.docker.com/r/sameli/detkit
        :text-align: center
        :class-card: custom-card-link

Supported Platforms
===================

Successful installation and tests have been performed on the following platforms and Python/PyPy versions shown in the table below.

.. |y| unicode:: U+2714
.. |n| unicode:: U+2716

+----------+-------------------+-------+-------+-------+-------+-------+-------+-------+-------+-----------------+
| Platform | Arch              | Python Version                        | PyPy Version :sup:`1` | Continuous      |
+          |                   +-------+-------+-------+-------+-------+-------+-------+-------+ Integration     +
|          |                   |  3.9  |  3.10 |  3.11 |  3.12 |  3.13 |  3.8  |  3.9  |  3.10 |                 |
+==========+===================+=======+=======+=======+=======+=======+=======+=======+=======+=================+
| Linux    | X86-64            |  |y|  |  |y|  |  |y|  |  |y|  |  |y|  |  |y|  |  |y|  |  |y|  | |build-linux|   |
+          +-------------------+-------+-------+-------+-------+-------+-------+-------+-------+                 +
|          | AARCH-64          |  |y|  |  |y|  |  |y|  |  |y|  |  |y|  |  |y|  |  |y|  |  |y|  |                 |
+----------+-------------------+-------+-------+-------+-------+-------+-------+-------+-------+-----------------+
| macOS    | X86-64            |  |y|  |  |y|  |  |y|  |  |y|  |  |y|  |  |y|  |  |y|  |  |y|  | |build-macos|   |
+          +-------------------+-------+-------+-------+-------+-------+-------+-------+-------+                 +
|          | ARM-64            |  |y|  |  |y|  |  |y|  |  |y|  |  |y|  |  |y|  |  |y|  |  |y|  |                 |
+----------+-------------------+-------+-------+-------+-------+-------+-------+-------+-------+-----------------+
| Windows  | X86-64            |  |y|  |  |y|  |  |y|  |  |y|  |  |y|  |  |y|  |  |y|  |  |y|  | |build-windows| |
+          +-------------------+-------+-------+-------+-------+-------+-------+-------+-------+                 +
|          | ARM-64 :sup:`2`   |  |y|  |  |y|  |  |y|  |  |y|  |  |y|  |  |y|  |  |y|  |  |y|  |                 |
+----------+-------------------+-------+-------+-------+-------+-------+-------+-------+-------+-----------------+

.. |build-linux| image:: https://img.shields.io/github/actions/workflow/status/ameli/detkit/build-linux.yml
   :target: https://github.com/ameli/detkit/actions?query=workflow%3Abuild-linux 
.. |build-macos| image:: https://img.shields.io/github/actions/workflow/status/ameli/detkit/build-macos.yml
   :target: https://github.com/ameli/detkit/actions?query=workflow%3Abuild-macos
.. |build-windows| image:: https://img.shields.io/github/actions/workflow/status/ameli/detkit/build-windows.yml
   :target: https://github.com/ameli/detkit/actions?query=workflow%3Abuild-windows

Python wheels for |project| for all supported platforms and versions in the above are available through `PyPI <https://pypi.org/project/detkit/>`__ and `Anaconda Cloud <https://anaconda.org/s-ameli/detkit>`_. If you need |project| on other platforms, architectures, and Python or PyPy versions, `raise an issue <https://github.com/ameli/detkit/issues>`_ on GitHub and we build its Python Wheel for you.

.. line-block::

    :sup:`1. Wheels for PyPy are exclusively available for installation through pip and cannot be installed using conda.`
    :sup:`2. Wheels for Windows on ARM-64 architecture are exclusively available for installation through pip and cannot be installed using conda.`

Install
=======

|pypi| |conda|

.. grid:: 2

    .. grid-item-card:: 

        Install with ``pip`` from `PyPI <https://pypi.org/project/detkit/>`_:

        .. prompt:: bash
            
            pip install detkit

    .. grid-item-card::

        Install with ``conda`` from `Anaconda Cloud <https://anaconda.org/s-ameli/detkit>`_:

        .. prompt:: bash
            
            conda install -c s-ameli detkit

For complete installation guide, see:

.. toctree::
    :maxdepth: 2

    Install <install/install>

Docker
======

|docker-pull| |deploy-docker|

The docker image comes with a pre-installed |project|, an NVIDIA graphic driver, and a compatible version of CUDA Toolkit libraries.

.. grid:: 1

    .. grid-item-card::

        Pull docker image from `Docker Hub <https://hub.docker.com/r/sameli/detkit>`_:

        .. prompt:: bash
            
            docker pull sameli/detkit

For a complete guide, see:

.. toctree::
    :maxdepth: 2

    Docker <docker>
    
List of Functions
=================

.. autosummary::
    :recursive:
    :nosignatures:
    :template: autosummary/member.rst

    detkit.logdet
    detkit.loggdet
    detkit.logpdet
    detkit.memdet

See :ref:`api` for the full list of functions.

Tutorials
=========

|binder|

Launch an online interactive tutorial in `Jupyter notebook <https://mybinder.org/v2/gh/ameli/detkit/HEAD?filepath=notebooks%2FSpecial%20Functions.ipynb>`_.

.. toctree::
    :maxdepth: 1
    :hidden:

    API Reference <api>

Benchmarks
==========

See :ref:`benchmark test <benchmark>` for evaluating the numerical performance of the functions in real applications.

.. toctree::
    :maxdepth: 2
    :hidden:

    Benchmark <benchmark>

Features
========

|tokei-2| |languages|

* Functions are implemented with a novel algorithm described in [1]_.
* The underlying library is implemented in C++ and wrapped in Cython.
* An accurate count of computational FLOPs during the execution of functions can be measured.

How to Contribute
=================

We welcome contributions via `Github's pull request <https://github.com/ameli/detkit/pulls>`_. If you do not feel comfortable modifying the code, we also welcome feature request and bug report as `Github issues <https://github.com/ameli/detkit/issues>`_.

Related Projects
================

|project| is used in the following python packages:

.. grid:: 2

   .. grid-item-card:: |glearn-light| |glearn-dark|
       :link: https://ameli.github.io/glearn/index.html
       :text-align: center
       :class-card: custom-card-link
   
       A high-performance python package for machine learning using Gaussian process regression.

   .. grid-item-card:: |imate-light| |imate-dark|
       :link: https://ameli.github.io/imate/index.html
       :text-align: center
       :class-card: custom-card-link
   
       A high-performance python package for scalable randomized algorithms for matrix functions in machine learning.

.. How to Cite
.. include:: cite.rst

.. |pypi| image:: https://img.shields.io/pypi/v/detkit
   :target: https://pypi.org/project/detkit
.. |deploy-docs| image:: https://img.shields.io/github/actions/workflow/status/ameli/detkit/deploy-docs.yml?label=docs
   :target: https://github.com/ameli/detkit/actions?query=workflow%3Adeploy-docs
.. |deploy-docker| image:: https://img.shields.io/github/actions/workflow/status/ameli/detkit/deploy-docker.yml?label=build%20docker
   :target: https://github.com/ameli/detkit/actions?query=workflow%3Adeploy-docker
.. |codecov-devel| image:: https://img.shields.io/codecov/c/github/ameli/detkit
   :target: https://codecov.io/gh/ameli/detkit
.. |license| image:: https://img.shields.io/github/license/ameli/detkit
   :target: https://opensource.org/licenses/BSD-3-Clause
.. |implementation| image:: https://img.shields.io/pypi/implementation/detkit
.. |pyversions| image:: https://img.shields.io/pypi/pyversions/detkit
.. |format| image:: https://img.shields.io/pypi/format/detkit
.. |conda| image:: https://img.shields.io/conda/v/s-ameli/detkit
   :target: https://anaconda.org/s-ameli/detkit
.. |platforms| image:: https://img.shields.io/conda/pn/s-ameli/detkit?color=orange?label=platforms
   :target: https://anaconda.org/s-ameli/detkit
.. |conda-version| image:: https://img.shields.io/conda/v/s-ameli/detkit
   :target: https://anaconda.org/s-ameli/detkit
.. |binder| image:: https://mybinder.org/badge_logo.svg
   :target: https://mybinder.org/v2/gh/ameli/detkit/HEAD?filepath=notebooks%2FInterpolateTraceOfInverse.ipynb
.. |conda-downloads| image:: https://img.shields.io/conda/dn/s-ameli/detkit
   :target: https://anaconda.org/s-ameli/detkit
.. |tokei| image:: https://tokei.rs/b1/github/ameli/detkit?category=lines
   :target: https://github.com/ameli/detkit
.. |tokei-2| image:: https://img.shields.io/badge/code%20lines-22.6k-blue
   :target: https://github.com/ameli/detkit
.. |languages| image:: https://img.shields.io/github/languages/count/ameli/detkit
   :target: https://github.com/ameli/detkit
.. |docker-pull| image:: https://img.shields.io/docker/pulls/sameli/detkit?color=green&label=downloads
   :target: https://hub.docker.com/r/sameli/detkit
.. |glearn-light| image:: _static/images/icons/logo-glearn-light.svg
   :height: 30
   :class: only-light
.. |glearn-dark| image:: _static/images/icons/logo-glearn-dark.svg
   :height: 30
   :class: only-dark
.. |imate-light| image:: _static/images/icons/logo-imate-light.svg
   :height: 23
   :class: only-light
.. |imate-dark| image:: _static/images/icons/logo-imate-dark.svg
   :height: 23
   :class: only-dark
.. |detkit-light| image:: _static/images/icons/logo-detkit-light.svg
   :height: 27
   :class: only-light
.. |detkit-dark| image:: _static/images/icons/logo-detkit-dark.svg
   :height: 27
   :class: only-dark

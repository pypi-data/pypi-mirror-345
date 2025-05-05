******
|logo|
******

``detKit`` is a Python package for computing determinant functions of matrices.

Links
=====

* `Documentation <https://ameli.github.io/detkit>`__
* `PyPI <https://pypi.org/project/detkit/>`__
* `Anaconda <https://anaconda.org/s-ameli/detkit>`__
* `Docker Hub <https://hub.docker.com/r/sameli/detkit>`__
* `Github <https://github.com/ameli/detkit>`__

Install
=======

Install with ``pip``
--------------------

|pypi|

::

    pip install detkit

Install with ``conda``
----------------------

|conda-version|

::

    conda install s-ameli::detkit

Docker Image
------------

|docker-pull| |deploy-docker|

::

    docker pull sameli/detkit

Supported Platforms
===================

Successful installation and tests performed on the following operating systems, architectures, and Python and `PyPy <https://www.pypy.org/>`__ versions:

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

Python wheels for ``detkit`` for all supported platforms and versions in the above are available through `PyPI <https://pypi.org/project/detkit/>`__ and `Anaconda Cloud <https://anaconda.org/s-ameli/detkit>`__. If you need ``detkit`` on other platforms, architectures, and Python or PyPy versions, `raise an issue <https://github.com/ameli/detkit/issues>`__ on GitHub and we build its Python Wheel for you.

.. line-block::

    :sup:`1. Wheels for PyPy are exclusively available for installation through pip and cannot be installed using conda.`
    :sup:`2. Wheels for Windows on ARM-64 architecture are exclusively available for installation through pip and cannot be installed using conda.`

Documentation
=============

|deploy-docs| |binder|

See `documentation <https://ameli.github.io/detkit/index.html>`__ of the package.

Benchmark Test
==============

Read about the `benchmark test <https://ameli.github.io/detkit/benchmark.html>`__ of ``detkit`` in practical applications.

How to Contribute
=================

We welcome contributions via `GitHub's pull request <https://github.com/ameli/detkit/pulls>`__. If you do not feel comfortable modifying the code, we also welcome feature requests and bug reports as `GitHub issues <https://github.com/ameli/detkit/issues>`__.

How to Cite
===========

If you publish work that uses ``detkit``, please consider citing the manuscripts available `here <https://ameli.github.io/detkit/cite.html>`__.

License
=======

|license|

This project uses a `BSD 3-clause license <https://github.com/ameli/detkit/blob/main/LICENSE.txt>`__, in hopes that it will be accessible to most projects. If you require a different license, please raise an `issue <https://github.com/ameli/detkit/issues>`__ and we will consider a dual license.

.. |logo| image:: https://raw.githubusercontent.com/ameli/detkit/main/docs/source/_static/images/icons/logo-detkit-light.svg
   :width: 160
.. |license| image:: https://img.shields.io/github/license/ameli/detkit
   :target: https://opensource.org/licenses/BSD-3-Clause
.. |deploy-docs| image:: https://img.shields.io/github/actions/workflow/status/ameli/detkit/deploy-docs.yml?label=docs
   :target: https://github.com/ameli/detkit/actions?query=workflow%3Adeploy-docs
.. |binder| image:: https://mybinder.org/badge_logo.svg
   :target: https://mybinder.org/v2/gh/ameli/detkit/HEAD?filepath=notebooks%2Fquick_start.ipynb
.. |pypi| image:: https://img.shields.io/pypi/v/detkit
   :target: https://pypi.org/project/detkit/
.. |deploy-docker| image:: https://img.shields.io/github/actions/workflow/status/ameli/detkit/deploy-docker.yml?label=build%20docker
   :target: https://github.com/ameli/detkit/actions?query=workflow%3Adeploy-docker
.. |docker-pull| image:: https://img.shields.io/docker/pulls/sameli/detkit?color=green&label=downloads
   :target: https://hub.docker.com/r/sameli/detkit
.. |conda-version| image:: https://img.shields.io/conda/v/s-ameli/detkit
   :target: https://anaconda.org/s-ameli/detkit

.. _dependencies:

Runtime Dependencies
====================

The followings are dependencies used during the runtime of |project|. Note that, among these dependencies, `OpenMP` is **required**, while the rest of the dependencies are optional.

.. _dependencies_openmp:

OpenMP (`Required`)
-------------------

|project| requires OpenMP, which is typically included with most C++ compilers.

.. glossary::

    For **Linux** users:

        By installing a C++ compiler such as GCC, Clang, or Intel, you also obtain OpenMP as well. You may alternatively install ``libgomp`` (see below) without the need to install a full compiler.

    For **macOS** users:

        It's crucial to note that OpenMP is not part of the default Apple Xcode's LLVM compiler. Even if you have Apple Xcode LLVM compiler readily installed on macOS, you will still need to install OpenMP separately via ``libomp`` Homebrew package (see below) or as part of the *open source* `LLVM compiler <https://llvm.org/>`__, via ``llvm`` Homebrew package.

    For **Windows** users:

        OpenMP support depends on the compiler you choose; Microsoft Visual C++ supports OpenMP, but you may need to enable it explicitly.

Below are the specific installation for each operating system:

.. tab-set::

    .. tab-item:: Ubuntu/Debian
        :sync: ubuntu

        .. prompt:: bash

            sudo apt install libgomp1 -y

    .. tab-item:: CentOS 7
        :sync: centos

        .. prompt:: bash

            sudo yum install libgomp -y

    .. tab-item:: RHEL 9
        :sync: rhel

        .. prompt:: bash

            sudo dnf install libgomp -y

    .. tab-item:: macOS
        :sync: osx

        .. prompt:: bash

            sudo brew install libomp

.. note::

    In *macOS*, for ``libomp`` versions ``15`` and above, Homebrew installs OpenMP as *keg-only*. To utilize the OpenMP installation, you should establish the following symbolic links:

    .. prompt:: bash

        libomp_dir=$(brew --prefix libomp)
        ln -sf ${libomp_dir}/include/omp-tools.h  /usr/local/include/omp-tools.h
        ln -sf ${libomp_dir}/include/omp.h        /usr/local/include/omp.h
        ln -sf ${libomp_dir}/include/ompt.h       /usr/local/include/ompt.h
        ln -sf ${libomp_dir}/lib/libomp.a         /usr/local/lib/libomp.a
        ln -sf ${libomp_dir}/lib/libomp.dylib     /usr/local/lib/libomp.dylib

.. _perf_tool:

Perf Tool (`Optional`)
----------------------

|project| can count the FLOPs of computations if the argument ``flops=True`` is used in the functions (see :ref:`API Reference <api>`). To achieve this, the `Linux Performance Counter <https://perf.wiki.kernel.org/index.php/Main_Page>`_ tool, known as ``perf``, must be installed.

.. tab-set::

    .. tab-item:: Ubuntu/Debian
        :sync: ubuntu

        .. prompt:: bash

            sudo apt-get install linux-tools-common linux-tools-generic linux-tools-$(uname -r)

    .. tab-item:: CentOS 7
        :sync: centos

        .. prompt:: bash

            sudo yum install perf

    .. tab-item:: RHEL 9
        :sync: rhel

        .. prompt:: bash

            sudo dnf install perf

.. attention::

    The ``perf`` tool is not available on macOS or Windows.

Granting Permissions
~~~~~~~~~~~~~~~~~~~~

After installing ``perf``, grant the necessary permissions to the user to run it:

.. prompt:: bash

    sudo sh -c 'echo 1 >/proc/sys/kernel/perf_event_paranoid'

This setting is temporary and will be lost after a reboot. To make it permanent, use the following commands instead:

.. prompt:: bash

    echo "kernel.perf_event_paranoid = 1" | sudo tee -a /etc/sysctl.conf
    sudo sysctl -p

Testing the Perf Tool
~~~~~~~~~~~~~~~~~~~~~

You can test if the ``perf`` tool is working by running the following command:

.. prompt:: bash

    perf stat -e instructions:u dd if=/dev/zero of=/dev/null count=100000

Alternatively, you can test the ``perf`` tool directly with :func:`detkit.check_perf_support`:

.. code-block:: python

    >>> import detkit
    >>> detkit.check_perf_support()

If the ``perf`` tool is installed and configured properly, the output of either of the above commands should be like:

.. code-block::

    {
        'kernel_version': '6.8.0-51-generic',
        'perf_event_paranoid': 1,
        'perf_installed': True,
        'perf_working': True
    }

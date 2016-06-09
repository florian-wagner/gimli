Installation on Linux
---------------------

On Linux platforms, the most comfortable way to install pygimli is via the conda package manager contained in the Anaconda distribution (https://docs.continuum.io/anaconda/install#linux-install) or the lightweight alternative Miniconda (http://conda.pydata.org/miniconda.html).

.. code:: bash

    conda install -c gimli pygimli
    conda update -c gimli -f pygimli # for updates

If you are not using Anaconda, you can build pyGIMLi from source in the current directory via:

.. code:: bash

    curl -Ls install.pygimli.org | bash

This script accepts a few more options. For help see:

.. code:: bash

    curl -Ls install.pygimli.org | bash -s help

If something goes wrong please take a look at the error message. 
In most cases there is are missing or outdated packages.

Please look first in prerequisites :link here .. how?: on needed packages. 

If the installation fails you can try the following instructions for manual installation. 


Detailed Installation on Vanilla Debian
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

First install some of the necessary stuff. You will need subversion, git and hg to
retrieve the source files and some things for the tool-chain:

.. code-block:: bash

    sudo apt-get install subversion git cmake mercurial
    sudo apt-get install libboost-all-dev libblas-dev liblapack-dev

If you want to use the pyGIMLi (Python scripts, bindings and apps):

.. code-block:: bash

    sudo apt-get install python-numpy python-matplotlib
    sudo apt-get install libedit-dev clang-3.6-dev llvm-3.6-dev python3-dev


Create a directory for your installation, e.g., $HOME/src

.. code-block:: bash

    mkdir -p ~/src
    cd src
    mkdir -p gimli
    cd gimli

Checkout the current sources for libgimli:

.. code-block:: bash

    git clone https://github.com/gimli-org/gimli.git

We use cmake (http://www.cmake.org/) for compilation. We recommend using a
build directory parallel to the gimli (trunk) path:

.. code-block:: bash

    mkdir -p build

The main directory structure should looks like this:

.. code-block:: bash

    gimli/gimli
    gimli/build

Change to the build path

.. code-block:: bash

    cd build

and configure the build:

.. code-block:: bash

    cmake ../gimli

If the output complains some missing dependencies,
install these and repeat the the last step.

To build the library just run make

.. code-block:: bash

    make

To speed up the build process using more CPUs, use the -j flag, e.g.:

.. code-block:: bash

    make -j 8

The libraries will be installed in build/lib and some test applications are
installed in build/bin

If you want to build the python bindings, call

.. code-block:: bash

    make pygimli

You might add J=8 for using 8 jobs in parallel to speed up the build.
The library _pygimli_.so library will be copied into the source path
../gimli/python/pygimli in the subdirectory core.
To use the gimli installation there have to be set some environment variables:

.. code-block:: bash

    export PYTHONPATH=$PYTHONPATH:$HOME/src/gimli/gimli/python
    export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:$HOME/src/gimli/build/lib
    export PATH=$PATH:$HOME/src/gimli/build/bin

If you want to use the C++ command line applications, call

.. code-block:: bash

    make apps

Compiled binaries will be written to `build/bin`.

You can test the pygimli build with:

.. code-block:: bash

    python -c 'import pygimli as pg; print(pg.__version__)'

You can test your gimli build with:

.. code-block:: bash

    make check

Note that the test will be very silent if you don't have cppunit installed.


Example Installation on Ubuntu
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: bash

    sudo apt-get install subversion git cmake mercurial
    sudo apt-get install libboost-all-dev libblas-dev liblapack-dev libedit-dev
    sudo apt-get install python-matplotlib python-numpy

    mkdir -p ~/src/gimli
    cd ~/src/gimli
    git clone https://github.com/gimli-org/gimli.git

    mkdir -p build
    cd build
    cmake ../gimli
    make gimli
    make pygimli

Troubleshooting
^^^^^^^^^^^^^^^

If you experience runtime problems on starting pygimli like:

.. code-block:: bash

    ImportError: /usr/lib/libboost_python.so: undefined symbol: PyClass_Type

It may happen that CMake estimates the wrong libboost_python version by choosing py2 version instead of py3.
You can force cmake to select the correct version with:

.. code-block:: bash

    cmake ../gimli -DBoost_PYTHON_LIBRARY=/usr/lib64/libboost_python3.so

If the build misses libedit:

.. code-block:: bash

    /usr/bin/ld: cannot find -ledit

Install *libedit*, e.g. 'apt-get install libedit' on Debian/Ubuntu.


castXML
.......

If castXML (https://github.com/CastXML/CastXML/) complains about missing clang or llvm command, please go into 
$(GIMLISRC)/../thirdParty/build-XXX-XXX/castXML and try configure and build cmake manually

.. code-block:: bash
    
    CC=clang-3.6 CXX=clang++-3.6 cmake ../../src/castXML/
    make

If you build castXML manually you can provide this binary to cmake via

.. code-block:: bash
    
    cmake ../gimli -DCASTER_EXECUTABLE=$(PATH_TO_CASTXML)
    

Useful cmake settings
^^^^^^^^^^^^^^^^^^^^^

You can rebuild and update all local generated third party software by setting the CLEAN environment variable:

.. code-block:: bash

    CLEAN=1 cmake ../gimli

Use alternative c++ compiler.

.. code-block:: bash

    CC=clang CXX=clang++ cmake ../gimli

Define alternative python version.
On default the version of your active python version will be chosen.
You will need numpy and boost-python builds with your desired python version.

.. code-block:: bash

    cmake ../gimli -DPYVERSION=3.3

Build the library with debug and profiling flags

.. code-block:: bash

    cmake ../gimli -DCMAKE_BUILD_TYPE=Debug

Build the library with gcc build.in sanity check 

.. code-block:: bash

    cmake ../gimli -DCMAKE_BUILD_TYPE=Debug -DASAN=1


Useful make commands
^^^^^^^^^^^^^^^^^^^^^

More verbose build output to view the complete command line:

.. code-block:: bash

    make VERBOSE=1
 

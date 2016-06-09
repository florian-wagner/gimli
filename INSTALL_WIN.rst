Installation on Windows
-----------------------

First, you need a Linux-like command shell along with a gcc compiler. 
Although there might be different solutions (Cygwin, Git Bash, MinGW/MSYS),
we only support the MSYS2 (Minimal System 2) hosted at http://msys2.github.io/
As computers and modern Windows (>=7) are 64bit we only test this.
Avoid installing into strange Windows folders, e.g. c:\msys64 is fine.

You will also need a native python installation if you want to use pygimli. 
We recommend WinPython: http://winpython.github.io/#releases

After installing MSYS, start the console once so it builds your personal home directory
where you find a .bashrc file, e.g. in

.. code-block:: bash

    c:/msys64/home/YOUR_USERNAME

Edit .bashrc so that the WinPython installation path is added to your default PATH.

.. code-block:: bash

    export PATH=$PATH:/c/PATH_TO_YOUR_WINPYTHON/WinPython-64bit-3.5.1.2/python-3.5.1/

This is necessary since gimli needs to know valid python installation and version.

Ideally the following one-liner will suffice to compile pyGIMLi in the current directory.

**Note: The script will automatic take care of requirements and updates of MSYS2. 
And also needs to modify/patch some of the llvm system files.**

.. code:: bash

    curl -Ls install.pygimli.org | bash 

This script accepts a few more options. For help see

.. code:: bash

    curl -Ls install.pygimli.org | bash -s help

If everything runs fine, including some tests, the script will tell you some 
additional PATH and PYTHONPATH settings for your .bashrc to use pygimli inside
the console or any IDE like Spyder (coming along with WinPython).

If something goes wrong, please take a look on the error message. 

You can alse try the following instructions for manual installation. 

Manual installation
...................

Make sure to have an updated msys2 environment. Run at least:

.. code-block:: bash

    pacman -Sy

to update your local package databases. See https://sourceforge.net/p/msys2/wiki/MSYS2%20installation/
for further instructions.

To get a complete working toolchain you need some packages installed.

.. code-block:: bash

    pacman -S make tar git subversion mercurial unzip wget patch

.. code-block:: bash

    pacman -S mingw-w64-x86_64-cmake mingw-w64-x86_64-gcc mingw-w64-x86_64-gcc-fortran
    pacman -S mingw-w64-x86_64-openblas mingw-w64-x86_64-doxygen
    pacman -S mingw-w64-x86_64-llvm mingw-w64-x86_64-clang

The rest of the installation is like the linux way with some small differences.

Prepare the directory structure as described above:

The build is performed via cmake. While calling cmake *MSYS* users should tell
using the MSYS makefile generator:

.. code-block:: bash

    cmake ../trunk -G 'MSYS Makefiles' -DBLAS_LIBRARIES=/mingw64/lib/libopenblas.a

If cmake complains about missing python stuff, make sure the Python interpreter
is in your execution path. If openblas is not installed you should of course omit 
the last directive, then built-int lapack/blas are used or they are build from source.

To build the library, just run

.. code-block:: bash

    make

You might add the option -jN to use a number of N CPUs in parallel.
To build pygimli, run

.. code-block:: bash

    make pygimli

You might add J=N to use a number of N CPUs in parallel.
Building pygimli takes some time and you can grab a coffee (or two).
If it finishes without errors you just need to set the environment:
(note that pygimli is still built in-place, in pygimli/core)

.. code-block:: bash

    export PYTHONPATH=$PYTHONPATH:$HOME/src/gimli/gimli/python
    export PATH=$PATH:$HOME/src/gimli/build/lib
    export PATH=$PATH:$HOME/src/gimli/build/bin

If you want to use the C++ commandline applications, call

.. code-block:: bash

    make apps

Compiled binaries will be written to `build/bin`.

You can test the pygimli build with:

.. code-block:: bash

    python -c 'import pygimli as pg; print(pg.__version__)'


Using cmake with CodeBlocks
...........................

Codeblocks is a nice C++ IDE available on http://www.codeblocks.org/downloads/

Tested versions 13.12/16.01, each without integrated mingw but a real MinGW/MSYS.

To generate the codeblocks project files run

.. code-block:: bash

    cmake -G "CodeBlocks - MinGW Makefiles"

and open the libgimli.cbp with codeblocks. Set up your compiler and run Build All.

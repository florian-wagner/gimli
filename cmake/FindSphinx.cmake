# CMake find_package() Module for Sphinx documentation generator
# http://sphinx-doc.org/
#
# Example usage:
#
# find_package(Sphinx)
#
# If successful the following variables will be defined
# SPHINX_FOUND
# SPHINX_EXECUTABLE

find_program(SPHINX_EXECUTABLE
             NAMES
                sphinx-build sphinx-build2
             DOC
                "Path to sphinx-build executable")

find_program(SPHINX_APIBUILD
             NAMES
                sphinx-apidoc
             DOC
                "Path to sphinx-api build executable")


# Handle REQUIRED and QUIET arguments
# this will also set SPHINX_FOUND to true if SPHINX_EXECUTABLE exists
include(FindPackageHandleStandardArgs)
find_package_handle_standard_args(Sphinx
                                  "Failed to locate sphinx-build executable"
                                  SPHINX_EXECUTABLE)

find_package_handle_standard_args(Sphinx
                                  "Failed to locate sphinx-api build executable"
                                  SPHINX_APIBUILD)

# Provide options for controlling different types of output
option(SPHINX_HTML_OUTPUT "Build a single HTML with the whole content." ON )
option(SPHINX_LATEX_OUTPUT "Build LaTeX sources that can be compiled to a PDF document using pdflatex." OFF )

#  **************************************************************************  #
#   BornAgain: simulate and fit reflection and scattering
#
#   @file      source:     Wrap/Python/src/bornagain/__init__.py.in
#              configured: build/py/src/bornagain/__init__.py
#   @brief     Top-level __init__.py of Python module BornAgain.
#
#   @homepage  http://apps.jcns.fz-juelich.de/BornAgain
#   @license   GNU General Public License v3 or higher (see COPYING)
#   @copyright Forschungszentrum Juelich GmbH 2016
#   @authors   Scientific Computing Group at MLZ (see CITATION, AUTHORS)
#  **************************************************************************  #

version = (23, 0)
version_str = "23.0"

# import all available BornAgain functionality from subdirectory lib/
from .lib import *

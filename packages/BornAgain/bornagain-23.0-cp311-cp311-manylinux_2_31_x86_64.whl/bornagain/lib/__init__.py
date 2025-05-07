#  **************************************************************************  #
#   BornAgain: simulate and fit reflection and scattering
#
#   @file      source:    Wrap/Python/src/bornagain/lib/__init__.py
#              copied to: build/py/src/bornagain/lib/__init__.py
#   @brief     Python extensions of the SWIG-generated Python module bornagain.
#
#   @homepage  http://apps.jcns.fz-juelich.de/BornAgain
#   @license   GNU General Public License v3 or higher (see COPYING)
#   @copyright Forschungszentrum Juelich GmbH 2016
#   @authors   Scientific Computing Group at MLZ (see CITATION, AUTHORS)
#  **************************************************************************  #

import sys, os

# NOTE: Adding the path to Python path is required for the automatically-built SWIG wrappers
BA_LIBPATH = os.path.dirname(__file__)  # BornAgain shared libs
BA_EXTRALIBPATH = os.path.join(BA_LIBPATH, 'extra')  # Extra dependencies

sys.path.append(BA_LIBPATH)
sys.path.append(BA_EXTRALIBPATH)
if sys.platform == 'win32':
    os.add_dll_directory(BA_EXTRALIBPATH)

# import all available BornAgain functionality
from libBornAgainBase import *
from libBornAgainFit import *
from libBornAgainParam import *
from libBornAgainSample import *
from libBornAgainResample import *
from libBornAgainDevice import *
from libBornAgainSim import *

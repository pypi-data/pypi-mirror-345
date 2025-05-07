#  **************************************************************************  #
"""
#   BornAgain: simulate and fit reflection and scattering
#
#   @file      Wrap/Python/ba_check.py
#   @brief     Infrastructure for persistence tests.
#
#   @homepage  http://apps.jcns.fz-juelich.de/BornAgain
#   @license   GNU General Public License v3 or higher (see COPYING)
#   @copyright Forschungszentrum Juelich GmbH 2016
#   @authors   Scientific Computing Group at MLZ (see CITATION, AUTHORS)
"""
#  **************************************************************************  #

import math, sys
import bornagain as ba

def matches_reference(result, fname, tolerance, reference, subname=""):
    """
    Check simulation result against reference.
    Used internally.
    """

    if not tolerance or not 'reference':
        print(f"{fname}: no tolerance or no reference")
        return True

    reffile = reference + subname + ".int"
    ok = ba.dataMatchesFile(result, reffile, tolerance)
    print(f"{fname} vs {reffile}, tol={tolerance} => ok={ok}")
    return ok

def persistence_test(result):
    for arg in sys.argv[1:]:
        s = arg.split("=")
        if len(s) != 2:
            raise Exception(f"command-line argument '{arg}' does not have form key=value")
        if s[0]=='datfile':
            datfile = s[1]
        elif s[0]=='reference':
            reference = s[1]
        elif s[0]=='tolerance':
            tolerance = float(s[1])
        else:
            raise Exception(f"unexpected argument '{arg}'")

    try:
        datfile
        reference
    except:
        raise Exception("missing some obligatory argument")
    assert(tolerance>0)
    assert(tolerance<1)

    if isinstance(result, list):
        nDigits = int(math.log10(len(result))) + 1
        formatN = "%" + str(nDigits) + "i"

        ok = True
        for i, one_result in enumerate(result):
            ok = ok and matches_reference(one_result, datfile, tolerance, reference, "." + (formatN % i))

        if not ok:
            print("To overwrite references:")
            for i, one_result in enumerate(one_result):
                outfile = fname + "." + (formatN % i) + ".int"
                reffile = reference + "." + (formatN % i) + ".int"
                ba.writeDatafield(one_result, outfile)
                print(f"cp -f {outfile} {reffile}")

            raise Exception("No agreement between result and reference")

    else:
        if not matches_reference(result, datfile, tolerance, reference):
            outfile = datfile + ".int"
            reffile = reference + ".int"
            ba.writeDatafield(result, outfile)
            print(f"To overwrite reference:\ncp -f {outfile} {reffile}")
            raise Exception("No agreement between result and reference")

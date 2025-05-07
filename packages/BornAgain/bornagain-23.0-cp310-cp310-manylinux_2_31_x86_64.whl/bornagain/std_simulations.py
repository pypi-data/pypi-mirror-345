"""
BornAgain collection of standard simulation setups.
"""
import bornagain as ba
from bornagain import deg, angstrom


def sas(sample, n):
    """
    Returns a standard simulation in small-angle scattering geometry.
    Incident beam is almost horizontal.
    """
    beam = ba.Beam(1, 1*angstrom, 1e-8*deg)
    det = ba.SphericalDetector(n, -4.5*deg, 4.5*deg, n, -4.5*deg, 4.5*deg)
    return ba.ScatteringSimulation(beam, sample, det)

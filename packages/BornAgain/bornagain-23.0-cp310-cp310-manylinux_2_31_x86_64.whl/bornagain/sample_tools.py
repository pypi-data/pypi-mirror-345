"""
BornAgain Python tools to inspect or modify sample.
"""
import bornagain as ba


def materialProfile(sample, n_points=400, z_min=None, z_max=None):
    """
    Creates a material profile from the given sample. If no limits are given,
    it will provide sensible default values, considering the included particles and
    interface roughnesses.
    :param sample: bornagain.MultiLayer object
    :param n_points: number of points to generate
    :param z_min: starting value for z
    :param z_max: ending value for z
    :return: numpy arrays containing z positions and the complex material values in those positions
    """
    def_z_min, def_z_max = ba.defaultMaterialProfileLimits(sample)
    z_min = def_z_min if z_min is None else z_min
    z_max = def_z_max if z_max is None else z_max
    z_points = ba.generateZValues(n_points, z_min, z_max)
    material_values = ba.materialProfileSLD(sample, n_points, z_min, z_max)
    return (z_points, material_values)

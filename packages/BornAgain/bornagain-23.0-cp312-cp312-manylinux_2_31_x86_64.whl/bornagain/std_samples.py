"""
BornAgain collection of standard sample.
"""
import bornagain as ba
from bornagain import deg, nm


def alternating_layers():
    """
    Returns sample sample consisting of 20 alternating Ti and Ni layers.
    """

    # Define materials
    material_ambient = ba.MaterialBySLD("Vacuum", 0, 0)
    material_ti = ba.MaterialBySLD("Ti", -1.9493e-06, 0)
    material_ni = ba.MaterialBySLD("Ni", 9.4245e-06, 0)
    material_substrate = ba.MaterialBySLD("SiSubstrate", 2.0704e-06, 0)

    # Define layers
    ambient_layer = ba.Layer(material_ambient)
    ti_layer = ba.Layer(material_ti, 3*nm)
    ni_layer = ba.Layer(material_ni, 7*nm)
    substrate_layer = ba.Layer(material_substrate)

    # Define stack
    n_repetitions = 10
    stack = ba.LayerStack(n_repetitions)
    stack.addLayer(ti_layer)
    stack.addLayer(ni_layer)

    # Define sample
    sample = ba.Sample()
    sample.addLayer(ambient_layer)
    sample.addStack(stack)
    sample.addLayer(substrate_layer)

    return sample


def substrate_plus_particle(particle):
    """
    Returns sample consisting of a substrate, and uncorrelated particles on top.
    """

    # Define material
    material_substrate = ba.RefractiveMaterial("Substrate", 6e-6, 2e-08)

    # Define particle layouts
    layout = ba.ParticleLayout()
    layout.addParticle(particle)
    layout.setTotalParticleSurfaceDensity(0.01)

    # Define layers
    layer_1 = ba.Layer(ba.Vacuum())
    layer_1.addLayout(layout)
    layer_2 = ba.Layer(material_substrate)

    # Define sample
    sample = ba.Sample()
    sample.addLayer(layer_1)
    sample.addLayer(layer_2)

    return sample


def cylinders():
    """
    Returns sample consisting of dilute cylinders on substrate.
    """
    mat = ba.RefractiveMaterial("Particle", 6e-4, 2e-08)
    ff = ba.Cylinder(5*nm, 5*nm)
    particle = ba.Particle(mat, ff)

    return substrate_plus_particle(particle)


def sas_sample_with_particle(particle):
    """
    Build and return a homogeneous sample containing uncorrelated particles.
    """

    layout = ba.ParticleLayout()
    layout.addParticle(particle)

    vacuum_layer = ba.Layer(ba.Vacuum())
    vacuum_layer.addLayout(layout)

    sample = ba.Sample()
    sample.addLayer(vacuum_layer)
    return sample

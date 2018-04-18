#   TEMPLATE FILE FOR FAST-SPIKING CORTICAL INTERNEURON
#                REGULAR-SPIKING CORTICAL PYRAMIDAL CELL
#
#
#   One compartment model and currents derived from:
#
#  Pospischil, M., Toledo-Rodriguez, M., Monier, C., Piwkowska, Z.,
#   Bal, T., Fregnac, Y., Markram, H. and Destexhe, A.
#   Minimal Hodgkin-Huxley type models for different classes of
#   cortical and thalamic neurons.
#   Biological Cybernetics 99: 427-441, 2008.
#
#   - one compartment model
#   - passive
#   - HH: Traub
#
#   Alain Destexhe, CNRS, 2008

from neuron import h

class sPY():
    """ Defining template for one-compartment sPY cell. """
    def __init__(self):
        self.soma = h.Section()

        v_potassium = -100
        v_sodium = 50

        self.soma.Ra = 100
        self.soma.nseg = 1
        self.soma.diam = 96
        self.soma.L = 96
        self.soma.cm = 1

        self.soma.insert('pas')
        self.soma.e_pas = -70
        self.soma.g_pas = 0.0001

        self.soma.insert('hh2')
        self.soma.ek = v_potassium
        self.soma.ena = v_sodium
        self.soma.vtraub_hh2 = -55
        self.soma.gnabar_hh2 = 0.05
        self.soma.gkbar_hh2 = 0.005

        self.soma.insert('im')
        self.soma.gkbar_im = 7e-5



class sIN():
    """ Defining template for one-compartment sIN cell. """
    def __init__(self):
        self.soma = h.Section()

        v_potassium = -100
        v_sodium = 50

        self.soma.Ra = 100
        self.soma.nseg = 1
        self.soma.diam = 67
        self.soma.L = 67
        self.soma.cm = 1

        self.soma.insert('pas')
        self.soma.e_pas = -70
        self.soma.g_pas = 5e-5
        self.soma.g_pas = 0.00015

        self.soma.insert('hh2')
        self.soma.ek = v_potassium
        self.soma.ena = v_sodium
        self.soma.vtraub_hh2 = -55
        self.soma.gnabar_hh2 = 0.05
        self.soma.gkbar_hh2 = 0.01

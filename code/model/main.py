import numpy as np
import neuron
from model.L23_templates import sPY, sIN

h = neuron.h

def load_l23_neurons(nr_neurons):
    """ Function for creating L2/3 neuron.

    output:
        L23_neurons: list containing all L2/3 neurons.
    """

    l23_neurons = []

    nr_neurons_inh = nr_neurons['GABAa'] + nr_neurons['GABAb']
    nr_neurons_exc = nr_neurons['AMPA'] + nr_neurons['NMDA']

    for _ in range(nr_neurons_exc):      # create excitatory L2/3 neurons
        l23_neurons.append(sPY())        # load sPY template
    for _ in range(nr_neurons_inh):      # create inhibitory L2/3 neurons
        l23_neurons.append(sIN())        # load sIN template

    return l23_neurons


def load_l5_cell(params):
    """
    Function for loading the morphology of the L5 cell and appending a long
    axon for epidural recordings.

    input:
        p: simulation parameters
    output:
        axon1 (neuron section): the added long axon for recording
    """

    h.load_file(params.l5_file)        # load L5 cell from file
    h.axon.L = params.axon_L             # modify original axon geometry
    h.axon.diam = params.axon_diam

    n_axon_seg = 200
    h('create myelin[%i], node[%i]' %(n_axon_seg, n_axon_seg))

    secs = list(h.allsec())
    myelin = [s for s in secs if "myelin[" in s.name()]
    nodes = [s for s in secs if "node[" in s.name()]

    for sec in myelin:
        sec.nseg = 5
        sec.L = 100.
        sec.diam = 3.

    for sec in nodes:
        sec.nseg = 1
        sec.L = 1.0
        sec.diam = 1.5

    h.myelin[0].connect(h.axon, 1, 0)
    h.node[0].connect(h.myelin[0], 1, 0)

    for i in range(n_axon_seg-1):
        h.myelin[i+1].connect(h.node[i], 1, 0)
        h.node[i+1].connect(h.myelin[i+1], 1, 0)

    for sec in myelin:
        sec.insert('pas')
        sec.cm = params.myelin_cm
        sec.e_pas = params.e_pas
        sec.g_pas = params.g_pas
        sec.insert('hh3')
        sec.gnabar_hh3 = params.axon_na
        sec.gkbar_hh3 = params.axon_k1
        sec.gkbar2_hh3 = params.axon_k2
        sec.insert('kdr')
        sec.gbar_kdr = params.axon_kdr

    for sec in nodes:
        sec.insert('pas')
        sec.cm = params.cm
        sec.g_pas = params.g_pas_node
        sec.e_pas = params.e_pas
        sec.insert('hh3')
        sec.gnabar_hh3 = params.axon_na
        sec.gkbar_hh3 = params.axon_k1
        sec.gkbar2_hh3 = params.axon_k2
        sec.gl_hh3 = params.axon_gl
        sec.insert('kdr')
        sec.gbar_kdr = params.axon_kdr

    axon1 = myelin + nodes

    return axon1


def load_membrane_mechanisms(dends, axon1, params):
    """
    function for setting up the membrane mechanisms and their parameters

    input:
        dends (list): list of all dendrite sections
        axon1 (neuron section): the long axon
    """

    h.tauh_hh3 = params.tauh_hh3
    h.sN_hh3 = params.sN_hh3

    for sec in dends:               # add HH and leakage to all dendrites
        sec.nseg = params.dend_nseg
        sec.insert('pas')
        sec.e_pas = params.e_pas
        sec.g_pas = params.g_pas
        sec.cm = params.cm
        sec.insert('hh3')
        sec.gkbar_hh3 = params.apic_k1
        sec.gkbar2_hh3 = params.apic_k2
        sec.gnabar_hh3 = params.apic_na
        sec.gl_hh3 = params.apic_gl
        sec.insert('kdr')
        sec.gbar_kdr = params.apic_kdr

    h.soma.insert('hh3')            # add HH and leakage to the soma
    h.soma.gnabar_hh3 = params.soma_na
    h.soma.gkbar_hh3 = params.soma_k1
    h.soma.gkbar2_hh3 = params.soma_k2
    h.soma.gl_hh3 = params.soma_gl
    h.soma.nseg = params.soma_nseg
    h.soma.insert('pas')
    h.soma.e_pas = params.e_pas
    h.soma.g_pas = params.g_pas
    h.soma.cm = params.cm
    h.soma.insert('kdr')
    h.soma.gbar_kdr = params.soma_kdr

    h.axon.insert('hh3')            # add HH, dr type K current, and leakage to the original axon
    h.axon.gnabar_hh3 = params.axon_na
    h.axon.gkbar_hh3 = params.axon_k1
    h.axon.gkbar2_hh3 = params.axon_k2
    h.axon.gl_hh3 = params.axon_gl
    h.axon.insert('kdr')
    h.axon.gbar_kdr = params.axon_kdr
    h.axon.nseg = params.axon_nseg
    h.axon.insert('pas')
    h.axon.e_pas = params.e_pas
    h.axon.g_pas = params.g_pas
    h.axon.cm = params.cm

    return dends, axon1


def run():
    """
    function for starting the simulation
    """
    h.init()
    time = np.arange(0, h.tstop, h.dt)

    for _ in time:
        h.fadvance()


def run_fast(fast_steps_per_ms, fast_tstop=295):
    """
    function for starting the simulation
    and for reducing build_up time of spontanous activity

    input: time and step parameters from file p
    """
    v_init = -70
    h.init(v_init)

    # faster build-up time
    # first 300 ms with large timesteps, following timesteps are standard size
    save_dtstep = h.steps_per_ms

    h.steps_per_ms = fast_steps_per_ms
    #fast_tstop = 300
    time1 = np.arange(0, fast_tstop+1./h.steps_per_ms, 1./h.steps_per_ms)

    h.steps_per_ms = save_dtstep
    time2 = np.arange(time1[-1] + 1./h.steps_per_ms, h.tstop, 1./h.steps_per_ms)

    time = np.concatenate((time1, time2))
    for time_point in time:
        h.cvode.active(0)      # cvode has to be inactive for changing size of dt in hoc

        if time_point == 0:
            h.dt = 2
            h.steps_per_ms = fast_steps_per_ms
            h.setdt()

        elif time_point == time2[0]:
            h.dt = 2               # random value which worked in tests
            h.steps_per_ms = save_dtstep
            h.setdt()
        h.fadvance()


def init_model(params):
    """
    Sets up the model: setting simulation parameters and loading cell files and
    membrane mechanisms.

    output:
           dends: list of dendrites
     L23 neurons: list of L2/3 neurons
           axon1: long axon object
    """

    h.load_file("stdrun.hoc")

    # setup simulation parameters
    h.steps_per_ms = params.steps_per_ms
    h.tstop = params.tstop
    h.runStopAt = params.tstop
    h.celsius = params.celsius

    # load the L5 cell, and get the L2/3 neurons and the long axon
    l23_neurons = load_l23_neurons(params.nr_neurons)
    axon1 = load_l5_cell(params)
    dends = list(h.dend) + list(h.apical)

    # load the membrane mechanisms
    dends, axon1 = load_membrane_mechanisms(dends, axon1, params)

    return l23_neurons, axon1, dends

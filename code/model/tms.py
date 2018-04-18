import numpy as np
import neuron
h = neuron.h


def pulse_l5_place(onset):
    """
    Function for creating the TMS pulse current injectors for L5 neurons.
    input:
        onset: onset of TMS in ms
    output:
        tms_pulse (list): list of TMS pulse current injectors for all neurons
    """

    tms_pulse = []
    pulse_axon = h.TMSpulse_bi(0.5, sec=h.soma)
    pulse_axon.onset = onset
    tms_pulse.append(pulse_axon)

    return tms_pulse


def pulse_l23_place(l23_neurons, onset):
    """
    Function for creating the TMS pulse current injectors for L2/3 neurons.
    input:
       l23_neurons: list of L2/3 neurons to be injected with pulse
           onset: onset of TMS in ms
    output:
        tms_pulse (list): list of TMS pulse current injectors for all neurons
    """

    tms_pulse = []
    for cell in l23_neurons:
        pulse_soma = h.TMSpulse_bi(0.5, sec=cell.soma)
        pulse_soma.onset = onset
        tms_pulse.append(pulse_soma)

    return tms_pulse


def pulse_l23_inject(tms_pulse, nr_neurons, intensity, scale_exc, scale_inh):
    """
    function for setting up the TMS pulse injectors for L2/3 neurons.

    input:
        tms_pulse: list of TMS pulse current injectors
    """

    gamma = 0.091755*intensity-8.05707

    nr_neurons_inh = nr_neurons['GABAa'] + nr_neurons['GABAb']
    nr_neurons_exc = nr_neurons['AMPA'] + nr_neurons['NMDA']

    tms_exc = gamma*np.random.exponential(scale_exc, nr_neurons_exc)
    tms_inh = gamma*np.random.exponential(scale_inh, nr_neurons_inh)

    # for numerical stability
    tms_exc[tms_exc > 500] = 500
    tms_inh[tms_inh > 500] = 500

    for i, cell_tms in enumerate(tms_pulse[:nr_neurons_exc]):
        cell_tms.imax = tms_exc[i]

    for i, cell_tms in enumerate(tms_pulse[nr_neurons_exc:]):
        cell_tms.imax = tms_inh[i]

    return tms_pulse, (tms_exc, tms_inh)


def pulse_l5_inject(tms_pulse, scale, intensity):
    """
    function for setting up the TMS pulse injectors for L5 Cell
    input:
        tms_pulse: list of TMS pulse current injectors
    """


    gamma = 0.091755*intensity-8.05707

    # generate amplitude from L5 TMS induced current amplitude distribution
    tms_pulse[0].imax = gamma*np.random.exponential(scale)
    return tms_pulse

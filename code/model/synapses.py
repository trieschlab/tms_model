import numpy as np
import neuron
h = neuron.h


def generate_weights(nr_neurons, syn_placement_uniform, \
    l23_5_weights_e, l23_5_weights_i, l23_5_weights_std, dendrites):
    """
    Generates synapse weights according to a lognormal distribution. Currently
    the weights are distributed uniformly on the L5 neuron.

    output:
        weights: dictionary with weight, location and type for each synapse

    """
    weights = []

    prob_length = np.array([section.L for section in dendrites])
    prob_length = prob_length / sum(prob_length)

    for stype in ['AMPA', 'NMDA', 'GABAa', 'GABAb']:

        nr_neurons_type = nr_neurons[stype]
        for _ in range(nr_neurons_type):

            weight = {}
            weight['name'] = stype
            weight['loc'] = np.random.choice(range(len(dendrites)), p=prob_length)
            weight['loc_name'] = dendrites[weight['loc']].name()
            weight['place'] = np.random.uniform(syn_placement_uniform[0], syn_placement_uniform[1])

            if stype in ['AMPA', 'NMDA']:
                # generate excitatory synaptic weight
                l23_5weight = np.random.lognormal(l23_5_weights_e, l23_5_weights_std)
            else:
                # generate inhibitory synaptic weight
                l23_5weight = np.random.lognormal(l23_5_weights_i, l23_5_weights_std)

            weight['weight'] = l23_5weight
            weights.append(weight)

    return weights


def l5_create(dendrites, l23_neurons, weights, syn_params, l23_5_delay):
    """
    function for generating synapses

    input:
           dendrites: list of dendrites
        L23 neurons: list of L2/3 neurons
         weights: weight dictionary from generate_syn_location_weights()

    output:
           synapses: list containing all synapses
        connections: list containin all connections (NetCon objects)
    """

    synapses = []
    connections = []

    for i, weight in enumerate(weights):

        synapse = h.ASyN_STD(weight['place'], sec=dendrites[weight['loc']])

        # set synapse parameters of a synapse
        stype = weight['name']
        synapse.tau1 = syn_params[stype]['TAU1']
        synapse.tau2 = syn_params[stype]['TAU2']
        synapse.gpeak = syn_params[stype]['GPEAK']
        synapse.e = syn_params[stype]['E']

        # short-term depression parameters
        synapse.d1 = syn_params['STD']['d1']
        synapse.tau_D1 = syn_params['STD']['tau_D1']

        # connect last (current) synapse with L2/3 cell soma
        current_conn = h.NetCon(l23_neurons[i].soma(0.5)._ref_v, \
                                synapse, 10, \
                                l23_5_delay, \
                                weight['weight'],\
                                sec=l23_neurons[i].soma)

        # and append to L5Connections
        synapses.append(synapse)
        connections.append(current_conn)

    return synapses, connections


def l23_create(l23_neurons, l23_synapes):
    """ Create synapses for transfering input spikes to L2/3 neurons."""

    synapses = []

    for cell in l23_neurons:

        synapse = h.FDSExp2Syn(0.5, sec=cell.soma)

        synapse.tau1 = l23_synapes['TAU1']
        synapse.tau2 = l23_synapes['TAU2']
        synapse.e = l23_synapes['E']

        synapse.f = 0
        synapse.d1 = 1  # no depression
        synapse.d2 = 1
        synapse.tau_F = 50   # ms
        synapse.tau_D1 = 200 # ms

        synapses.append(synapse)

    return synapses


def create_stimuli(weights, l23_synapses, phi, l23_rates, l23_shift, \
    mode='mu-rhythm-shift'):
    """ Create spikes according to specified rate and structure and connect
    to L2/3 neurons. """

    vec_stim_list = []
    stimuli = []
    connections = []

    for i, synapse in enumerate(l23_synapses):

        rate = l23_rates[weights[i]['name']]
        shift = l23_shift[weights[i]['name']]

        spikes = spiketrains(rate, mode=mode, phi=phi, const_freq=shift)
        spikes = h.Vector(spikes)

        player = h.VecStim()
        player.play(spikes)

        threshold = 0
        delay = 0
        weight = 0.03

        # connect last (current) synapse with L2/3 cell soma
        current_conn = h.NetCon(player,
                                synapse, threshold,
                                delay,
                                weight)

        # save all objects in lists
        connections.append(current_conn)
        vec_stim_list.append(player)
        stimuli.append(spikes)

    return connections, stimuli, vec_stim_list


def spiketrains(rate, mode='homogeneous', phi=0, const_freq=1):
    """ Create spike trains with different characteristics. Either homogeneous
        Poisson spiking, or spiking modulated by a sine wave.
    """

    if mode == 'homogeneous':
        spikes = np.random.rand(np.random.poisson(rate*h.tstop/1000.0))*h.tstop

    if mode == 'mu-rhythm-shift':
        sim_time = 0
        max_rate = rate*2
        mu_freq = 10 #Hz

        spikes = []
        while sim_time < h.tstop/1000.:
            sim_time = sim_time-np.log(np.random.rand())/max_rate
            lambda_t = rate*(np.sin(mu_freq*sim_time*2*np.pi+phi)+const_freq)
            if np.random.rand() < lambda_t/max_rate:
                spikes.append(sim_time*1000)

    spikes.sort()

    return spikes

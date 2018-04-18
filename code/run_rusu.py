import argparse
import importlib
import numpy as np
import neuron
import matplotlib.pyplot as plt
from model import helper, tms, synapses, main

h = neuron.h
h('objref nil')

parser = argparse.ArgumentParser()
parser.add_argument('-p', '--param', nargs='?', type=str, default=None, help='')
parser.add_argument('-i', '--intensity', nargs='?', type=float, default=120, help='')
arguments = parser.parse_args()
params = importlib.import_module(arguments.param[:-3].replace('/', '.'))

if __name__ == '__main__':

    # setting up for parallel computations
    size, rank, comm = helper.parallel_setup(params.parallel)

    # create results directory
    base_dir = '../results/single/'
    save_dir = helper.create_save_directory(rank, params.output_filename, base_dir)
    if comm:
        save_dir = comm.bcast(save_dir, root=0)

    # loading L2/3 and L5 neurons
    l23_neurons, axon1, dends = main.init_model(params)

    measures = ['L5_mem', 'L5_spikes']
    results = []

    for j in range(params.nr_trials):
        if rank == 0:
            print 'Starting simulation %02i/%02i' %(j+1, params.nr_trials)

        # creating synapse weights, weight placement is currently uniform
        syn_weights = synapses.generate_weights(params.nr_neurons, \
            params.syn_placement_uniform, params.l23_5_weights_e, \
            params.l23_5_weights_i, params.l23_5_weights_std, dends)

        # placing and plotting synapses
        l5_synapses, l5_connections = synapses.l5_create(dends, l23_neurons, \
            syn_weights, params.syn_params, params.l23_5_delay)

        # TMS pulse for stimulation L2/3 neuron
        tms_pulse_l23 = tms.pulse_l23_place(l23_neurons, params.onset)
        tms_pulse_l23 = tms.pulse_l23_inject(tms_pulse_l23, \
            params.nr_neurons, arguments.intensity, \
            params.TMS_I_l23_scale_exc, params.TMS_I_l23_scale_inh)

        # TMS pulse for stimulation L5 neuron
        tms_pulse_l5 = tms.pulse_l5_place(params.onset)
        tms_pulse_l5 = tms.pulse_l5_inject(tms_pulse_l5, \
            params.TMS_I_l5_scale, arguments.intensity)

        # set up record membrane potential of L5 and L2/3 neurons
        trial = helper.get_recordings(l23_neurons, axon1, measures)

        # run simulation
        main.run()
        trial = helper.convert_recordings(trial)
        results.append(trial)

    # plot model output
    L5_mem = np.array([trial['L5_mem'] for trial in results])
    response = np.mean(L5_mem, axis=0)
    response, sim_time = helper.convolve_l5_mem(trial['time'], response)

    plt.figure()
    plt.plot(sim_time, response)
    plt.xlim(0, sim_time[-1])
    plt.xlabel('time [ms]')
    plt.ylabel('model output [a.u.]')
    plt.show()

    # save results
    out = helper.save_results(save_dir, rank, size, results, syn_weights, params)

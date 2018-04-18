import argparse
import importlib
import numpy as np
import neuron
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
    base_dir = '../results/single/' + params.output_filename + '/'
    save_dir = helper.create_save_directory(rank, params.output_filename + \
            '_int_' + str(arguments.intensity), base_dir)
    if params.parallel == 1:
        save_dir = comm.bcast(save_dir, root=0)

    # loading L2/3 and L5 neurons
    l23_neurons, axon1, dends = main.init_model(params)

    results = []
    stim_phase_list = np.arange(params.stim_phase_list[0]/180., \
                                params.stim_phase_list[1]/180.,\
                                params.stim_phase_steps/180.)*np.pi

    shift = 0.8796
    stim_phase_shifted = stim_phase_list + shift

    measures = params.measures

    for _ in range(params.nr_trials):

        # creating synapse weights, weight placement is uniform w.r.t. length
        syn_weights = synapses.generate_weights(params.nr_neurons, \
        params.syn_placement_uniform, params.l23_5_weights_e, \
        params.l23_5_weights_i, params.l23_5_weights_std, dends)

        for i, stim_phase in enumerate(stim_phase_shifted):

            if rank == 0:
                print 'Starting simulation for phase=%.1f' %(stim_phase)

            # placing and plotting synapses
            l5Synapses, l5Connections = synapses.l5_create(dends, l23_neurons, \
                syn_weights, params.syn_params, params.l23_5_delay)

            l23_synapses = synapses.l23_create(l23_neurons, params.syn_params['L23'])

            l23_connections, l23_stimuli, l23_vecstims = \
                synapses.create_stimuli(syn_weights, l23_synapses, stim_phase, \
                    params.l23_rates, params.l23_shift, mode=params.mode)


            # TMS pulse
            tms_pulse_l23 = tms.pulse_l23_place(l23_neurons, params.onset)
            tms_pulse_l23 = tms.pulse_l23_inject(tms_pulse_l23, params.nr_neurons, \
                arguments.intensity, params.TMS_I_l23_scale_exc, params.TMS_I_l23_scale_inh)
            tms_pulse_l5 = tms.pulse_l5_place(params.onset)
            tms_pulse_l5 = tms.pulse_l5_inject(tms_pulse_l5, params.TMS_I_l5_scale, \
                arguments.intensity)

            trial = helper.get_recordings(l23_neurons, axon1, measures)
            trial['onset'] = params.onset
            trial['stim_phase'] = stim_phase

            # run simulation
            main.run_fast(5)

            trial = helper.convert_recordings(trial)
            results.append(trial)

    # save results
    out = helper.save_results(save_dir, rank, size, results, syn_weights, params)

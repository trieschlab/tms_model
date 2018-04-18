import time
import os
import numpy as np
import neuron

h = neuron.h
h('objref nil')

def convolve_l5_mem(sim_time, l5_membrane):
    """ Convolve L5 membrane potential with Gaussian kernel. """

    kernel_std = 30.0
    norm_const = 1/np.sqrt(2*np.pi*kernel_std)
    x_range = np.arange(-kernel_std, kernel_std, 1)
    kernel = norm_const*np.exp(-pow(x_range, 2)/(2*kernel_std))

    response = np.convolve(l5_membrane, kernel, 'valid')
    cut_time = sim_time[int(kernel_std):int(sim_time.shape[0])-int(kernel_std)+1]

    return response, cut_time

def get_recordings(l23_neurons, axon1, measures):
    """ Sets up NEURON objects for recordings of selected measures. """
    trial = {}
    sim_time = h.Vector()
    sim_time.record(h._ref_t)
    trial['time'] = sim_time

    axon_names = [sec.name() for sec in axon1]
    idx = axon_names.index("node[100]")  # record in the middle of long axon

    for measure in measures:

        if measure == 'L5_mem':
            l5_membrane = h.Vector()
            l5_membrane.record(axon1[idx](0.5)._ref_v)
            recording = l5_membrane

        elif measure == 'L5_spikes':
            l5_spikes = h.Vector()
            l5_spikes_nc = h.NetCon(axon1[idx](0.5)._ref_v, h.nil, sec=axon1[idx])
            l5_spikes_nc.threshold = 0
            l5_spikes_nc.record(l5_spikes)
            recording = l5_spikes


        elif measure == 'L23_spikes':
            l23_spikes = []
            for cell in l23_neurons:
                spike = h.Vector()
                spike_nc = h.NetCon(cell.soma(0.5)._ref_v, h.nil, sec=cell.soma)
                spike_nc.threshold = 0
                spike_nc.record(spike)
                l23_spikes.append(spike)
                recording = l23_spikes

        trial[measure] = recording

    return trial


def parallel_setup(parallel):
    """
    input:
        parallel : 1 for parallel usage with mpirun, 0 for single core
    """
    if parallel:
        if os.environ.has_key('DISPLAY'): # remove DISPLAY for use on cluster
            del os.environ['DISPLAY']
            import matplotlib
            matplotlib.use('Agg')           # important for use on clusters

        from mpi4py import MPI          # for parallelization
        comm = MPI.COMM_WORLD           # initiate communicator
        size = comm.Get_size()          # get number of workers
        rank = comm.Get_rank()          # worker id
                                    # rank==0: master
                                    # rank!=0: slaves
    else:
        rank = 0
        size = 0
        comm = None

    # use different seed for each worker
    np.random.seed(np.random.randint(256) *(rank + 1))

    return size, rank, comm


def save_parameters(params):
    """ Saving all parameters used for simulation in a dictionary. """
    param_dict = {}
    for key, value in vars(params).iteritems():
        if not key.startswith("__"):
            param_dict[key] = value
    return param_dict


def create_save_directory(rank, output_filename_prefix, base_dir):
    """ Create time-stamped directory for saving results. """
    if rank == 0:
        time_stamp = time.strftime("%Y%m%d-%H%M%S")
        save_dir = base_dir + '%s_networks_%s' %(output_filename_prefix, time_stamp)

        if not os.path.exists(save_dir):
            try:
                os.makedirs(save_dir)
            except OSError:
                pass

    else:
        save_dir = None

    return save_dir

def convert_recordings(trial):
    """ Convert nested results to numpy structures. """
    for key, value in trial.iteritems():
        if key in ['stimuli', 'L23_membrane', 'L23_spikes', 'synaptic_current']:
            trial[key] = [np.array(v) for v in value]
        else:
            trial[key] = np.array(value)
    return trial


def save_results(save_dir, rank, size, \
                            results, weights, params):
    """ Writing all results from one simulation into a structure. """
    output_filename = '%s_%i_%i' %(params.output_filename, rank+1, size)
    file_name = '%s/%s_results.npy' %(save_dir, output_filename)
    out = {}
    out['results'] = results
    out['weights'] = weights
    out['params'] = save_parameters(params)
    np.save(file_name, out)

    # save weights separately for reloading
    file_name = '%s/%s_weights.npy' %(save_dir, output_filename)
    np.save(file_name, weights)
    return out

# find_simulation

# register_simulation

import json
import argparse
import os
import math

simdata_path = os.path.dirname(__file__)+'/data/'

def find_simulation(params, chain_class, simdata_path=simdata_path+'simdata.json'):
    with open(simdata_path, 'r') as f:
        simdata = json.load(f)

    details_list = []
    for sim_id, details in simdata.items():
        if (all((params.get(key, None) == val) for key, val in details['parameters'].items()) and
        details['chain_class'] == chain_class):
            details_list.append((sim_id, details['csv_path'], details['status']))
        elif all(details['parameters'].get(key, None) == val for key, val in params.items()):
            details_list.append((sim_id, details['csv_path'], details['status']))
    
    return details_list

def register_simulation(params, chain_class, status='pending', simdata_path=simdata_path+'simdata.json'):
    try:
        with open(simdata_path, 'r') as f:
            simdata = json.load(f)
    except FileNotFoundError:
        simdata = {}

    sim_id = f'simulation_{len(simdata) + 1:04d}'
    csv_path = sim_id+'.csv'
    simdata[sim_id] = {
        'chain_class': chain_class,
        'parameters': params,
        'csv_path': csv_path,
        'status': status
    }

    with open(simdata_path, 'w') as f:
        json.dump(simdata, f, indent=4)

    return sim_id


def parse_args(arg_list: list[str] = None):

    parser = argparse.ArgumentParser(
        description="Run a telecommunication chain simulation",
        usage="rye run python sim.py [SIMULATION_PARAMETERS] [CHAIN_PARAMETERS]")

    sim_group = parser.add_argument_group("Simulation Parameters")
    sim_group.add_argument("--basic", action="store_true",
                            help="if set, uses the BasicChain object instead of OptimizedChain - "
                            "BasicChain is the unoptimized, less performing version of OptimizedChain")
    sim_group.add_argument("-f", "--force_simulation", action="store_true",
                            help="if set, force simulation and replace any existing datafile corresponding to simulation parameters")
    sim_group.add_argument("-s", "--sim_id", type=int, default=0,
			                help="if set, uses the simulation 'simulation_{SIM_ID}' - default to 0 (not an existing simulation)")
    sim_group.add_argument("--no_show", "--dont_show_graphs",
                            action="store_true", help="if set, don't show matplotlib graphs")
    sim_group.add_argument("--no_save", "--dont_save_graphs",
                            action="store_true", help="if set, don't save matplotlib graphs")
    sim_group.add_argument("--FIR", action="store_true", default=False,
                            help="if set, generates the FIR graph of chain")

    chain_group = parser.add_argument_group("Chain Parameters")
    chain_group.add_argument("-p", "--payload_len", type=int, default=50,
                              help="payload length of chain - default to 50")
    chain_group.add_argument("-n", "--n_packets", type=int, default=100,
                              help="number of packets of chain - default to 100")
    chain_group.add_argument("-m", "--cfo_Moose_N", type=int, default=4,
                              help="N parameter in Moose algorithm - max value is #bits in preamble / 2 - "
                              "default to 2 in OptimisedChain and 4 in BasicChain")
    chain_group.add_argument("-r", "--cfo_range", type=int, default=1e3,
                              help="CFO range- max value should be Bitrate / (2 * cfo_Moose_N) - default to 1e3 -  "
                              "higher values could greatly decrease performances")
    chain_group.add_argument("-pre", "--enable_preamble_detect",
                              action="store_true", help="if set, enables preamble detection")
    chain_group.add_argument("-cfo", "--enable_cfo_estimation",
                              action="store_true", help="if set, enables CFO estimation")
    chain_group.add_argument("-sto", "--enable_sto_estimation",
                              action="store_true", help="if set, enables STO estimation")
    
    args = parser.parse_args(arg_list)

    sim_params = argparse.Namespace()
    chain_params = argparse.Namespace()

    for action in sim_group._group_actions:
        setattr(sim_params, action.dest, getattr(args, action.dest))
    for action in chain_group._group_actions:
        setattr(chain_params, action.dest, getattr(args, action.dest))

    return sim_params, chain_params

if __name__ == '__main__':
    params = {'p': 50, 'n': 100000, 'pre_det': True, 'sto_est': True}
    for csv_path, status in find_simulation(params):
        print(f'CSV Path: {csv_path}, Status: {status}')
    sim_id = register_simulation(params, status='completed')
    print(f'Simulation registered as: {sim_id}')
    

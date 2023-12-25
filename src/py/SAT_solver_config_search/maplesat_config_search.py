import numpy as np
import argparse
import os
import subprocess
import multiprocessing


def generate_combinations_recursive(settings, current=[]):
    if not settings:
        yield ' '.join(current)
        return
    key = next(iter(settings))
    for value in settings[key]:
        yield from generate_combinations_recursive(settings={k: v for k, v in settings.items() if k != key},
                                                   current=current + [value])


def get_configs():
    settings = {}
    settings['luby'] = [" -luby ", " -no-luby"]
    settings['rnd_init'] = [" -rnd-init ", " -no-rnd-init"]
    settings['gc_frac'] = [f" -gc-frac={x:.4f}" for x in np.random.permutation(np.arange(0.1, 0.2, 0.1))]
    settings['rinc'] = [f" -rinc={x}" for x in np.random.permutation(np.arange(2, 3, 1))]
    settings['step_size'] = [f" -step-size={x:.4f}" for x in np.random.permutation(np.arange(0.1, 0.2, 0.1))]
    settings['step_size_dec'] = [f" -step-size-dec={x:.4f}" for x in np.random.permutation(np.arange(0.1, 0.2, 0.1))]
    settings['min_step_size'] = [f" -min-step-size={x:.4f}" for x in np.random.permutation(np.arange(0.1, 0.2, 0.1))]
    settings['rnd_freq'] = [f" -rnd-freq={x:.4f}" for x in np.random.permutation(np.arange(0.1, 0.2, 0.1))]
    settings['ccmin_mode'] = list(np.random.permutation([" -ccmin-mode=0", " -ccmin-mode=1", " -ccmin-mode=2"]))
    settings['rfirst'] = [f" -rfirst={x}" for x in np.random.permutation(np.arange(1, 500, 250))]
    settings['phase_saving'] = list(np.random.permutation([" -phase-saving=0", " -phase-saving=1", " -phase-saving=2"]))
    settings['pre'] = list(np.random.permutation([" -pre", " -no-pre"]))
    settings['el'] = list(np.random.permutation([" -elim", " -no-elim"]))
    settings['rchk'] = list(np.random.permutation([" -rcheck", " -no-rcheck"]))
    settings['simp_gc_frac'] = [f" -simp-gc-frac={x:.4f}" for x in np.random.permutation(np.arange(0.1, 0.2, 0.1))]
    settings['sub_lim'] = [f" -sub-lim={x}" for x in np.random.permutation(np.arange(-1, 1001, 500))]
    settings['cl_lim'] = [f" -cl-lim={x}" for x in np.random.permutation(np.arange(-1, 21, 10))]
    settings['grow'] = [f" -grow={x:.4f}" for x in np.random.permutation(np.arange(0, 2, 1))]

    for config in generate_combinations_recursive(settings):
        yield config


def execute_trial(args):
    """Execute a C++ program with the given configuration and file."""
    idx, base_cmd, config, file, output_dir = args

    command = f"{base_cmd} {config} {file}"
    output_file = os.path.join(output_dir, f"output_{idx}.txt")

    # Redirect stdout and stderr to the output file
    with open(output_file, 'w') as outfile:
        outfile.write(f"id: {idx}\n")
        outfile.write(f"File: {file}\n")
        outfile.write(f"Config: {config}\n")

        subprocess.run(command, shell=True, stdout=outfile, stderr=outfile)


def main():
    parser = argparse.ArgumentParser(description='Execute multiple configurations in parallel and save the results.')
    parser.add_argument('--cmd_base', required=False, default="./maplesat", type=str, help='base command to execute')
    parser.add_argument('--dir', required=True, type=str, help='directory in which input_files and output_files exist')
    parser.add_argument('--n_max_trials', required=False, default=10, type=int, help='maximum number of trials')
    parser.add_argument('--n_cores', required=False, default=-1, type=int,
                        help='number of processes to be executed in parallel')
    args = parser.parse_args()

    base_cmd = args.cmd_base
    directory_path = args.dir
    num_processes = multiprocessing.cpu_count() if args.n_cores <= 0 else args.n_cores
    n_max_trials = args.n_max_trials

    input_dir = directory_path + "input_files/"
    output_dir = directory_path + "output_files/"

    files = [os.path.join(input_dir, item) for item in os.listdir(input_dir)]
    configurations = []
    for config in get_configs():
        if n_max_trials>=0 and len(configurations) >= n_max_trials:
            break
        configurations.append(config)

    os.makedirs(output_dir, exist_ok=True)

    args_list = []
    idx = 0
    for file in files:
        for config in configurations:
            idx += 1
            args_list.append((idx, base_cmd, config, file, output_dir))

    with multiprocessing.Pool(processes=num_processes) as pool:
        pool.map(execute_trial, args_list)

    print("Done.")


if __name__ == "__main__":
    main()

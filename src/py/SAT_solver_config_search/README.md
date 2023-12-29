
Notes regarding maplesat_config_search.py:
 
This code is written to be executed on Linux. A few modifications might be needed for other operating systems.

Its only requirement is 'numpy'.

Please adjust get_configs() function to fit your needs.

In some directory, create two folders named input_files and output_files. 

In the input_files put .cnf files you want to conduct the experiment on them, and let output_files be an empty folder.

If the python script is on the same directory as maplesat it is fine. Otherwise, you should provide the maplesat's path using '-cmd_base' argument.


examples:

python3 maplesat_config_search.py --help

python3 maplesat_config_search.py --cmd_base='./maplesat' --dir='/media/sf_shared/' --n_max_trials=10

python3 maplesat_config_search.py --dir='/media/sf_shared/' --n_cores=2

python maplesat_config_search.py --dir='' --n_max_trials=3 --n_cores=2


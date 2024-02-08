

run.sh is responisble for generating all solutions in parallel, and concatenating results into one file.
Add run.sh to the original unidom's main directory, change the parameters if needed, and execute ./run.sh.
Note, when using multiple processes, unidom's generate all might produce some commpletely equivalent solutions.
Thus, if needed, one should add a post-processing step to manage this case. 
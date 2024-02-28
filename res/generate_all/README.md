# Gamma

All optimal solutions for 7<=n<=18 are generated.

These solutions are not up to isomorphism, but they simply include all solutions. Thus, isomorphism rejection should be done as a post processing step if one wishes to count the number of solutions up to isomorphism.

For some ns, results stored in one single file.

For others, the results stored in multiple files with suffix _part_X.


In each file, each solution is displayed as a chessboard in which Q stands for wherhe queen has been placed, x shows a square exlcuded from candidate set in that state of the search, and other squares annotated with '-' symbol means they are empty.

In each file, each solution seperated with a ';' from the subsequent one.

generate_all_v1: related to buggy version

generate_all_v2: related to fixed/corrected version
#!/bin/bash

n_small=10
gamma=5
num_processes=5
split_depth=2

files=()

for ((i=0; i<$num_processes; i++)); do
    ./unidom -I queen -n $n_small -S MDD_all -u $gamma -mod $num_processes -res $i -resmod_depth $split_depth -O output_all > "all_${n_small}_${gamma}_$i.txt" 2>&1 &
    files+=("all_${n_small}_${gamma}_$i.txt")
done

wait

echo "n_small=$n_small, gamma=$gamma, num_processes=$num_processes, split_depth=$split_depth" > "all_${n_small}_${gamma}.txt"
cat "${files[@]}" >> "all_${n_small}_${gamma}.txt"

rm "${files[@]}"


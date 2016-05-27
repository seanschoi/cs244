#!/bin/bash

for t in fattree waxman smallworld dense
do
    for test in 1 2 3
    do
        for sub in none subspace
        do
            sudo ./run.sh $t 30 $test $sub > $t_$test_$sub.txt
            chmod +w $t_$test_$sub.txt
        done
    done
done

#!/bin/bash

sbatch --cpus-per-task=4 --mem=10G -t 6000 --mail-type=END --mail-user=lytr777@mail.ru main.sh p2 configurations/perf_test.json

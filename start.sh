#!/bin/bash

sbatch --cpus-per-task=4 --mem=10G -t 8000 --mail-type=END --mail-user=lytr777@mail.ru main.sh 5 configurations/tabu.json
sbatch --cpus-per-task=4 --mem=10G -t 8000 --mail-type=END --mail-user=lytr777@mail.ru main.sh 6 configurations/tabu.json
sbatch --cpus-per-task=4 --mem=10G -t 8000 --mail-type=END --mail-user=lytr777@mail.ru main.sh 7 configurations/tabu.json
sbatch --cpus-per-task=4 --mem=10G -t 8000 --mail-type=END --mail-user=lytr777@mail.ru main.sh 8 configurations/tabu.json

#!/bin/bash

sbatch --cpus-per-task=4 --mem=10G -t 4000 --mail-type=END --mail-user=lytr777@mail.ru main.sh 5
sbatch --cpus-per-task=4 --mem=10G -t 4000 --mail-type=END --mail-user=lytr777@mail.ru main.sh 6
sbatch --cpus-per-task=4 --mem=10G -t 4000 --mail-type=END --mail-user=lytr777@mail.ru main.sh 7
sbatch --cpus-per-task=4 --mem=10G -t 4000 --mail-type=END --mail-user=lytr777@mail.ru main.sh 8

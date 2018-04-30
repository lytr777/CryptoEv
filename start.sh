#!/bin/bash

sbatch --cpus-per-task=4 --mem=10G -t 6000 --mail-type=END --mail-user=lytr777@mail.ru main.sh 9
sbatch --cpus-per-task=4 --mem=10G -t 6000 --mail-type=END --mail-user=lytr777@mail.ru main.sh 10
sbatch --cpus-per-task=4 --mem=10G -t 6000 --mail-type=END --mail-user=lytr777@mail.ru main.sh 11
sbatch --cpus-per-task=4 --mem=10G -t 6000 --mail-type=END --mail-user=lytr777@mail.ru main.sh 12

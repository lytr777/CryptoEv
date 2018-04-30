#!/bin/bash

sbatch --cpus-per-task=4 --mem=10G -t 6000 --mail-type=END --mail-user=lytr777@mail.ru main.sh 13
sbatch --cpus-per-task=4 --mem=10G -t 6000 --mail-type=END --mail-user=lytr777@mail.ru main.sh 14
sbatch --cpus-per-task=4 --mem=10G -t 6000 --mail-type=END --mail-user=lytr777@mail.ru main.sh 15
sbatch --cpus-per-task=4 --mem=10G -t 6000 --mail-type=END --mail-user=lytr777@mail.ru main.sh 16

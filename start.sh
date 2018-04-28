#!/bin/bash

sbatch --cpus-per-task=4 --mem=10G -t 6000 --mail-type=END --mail-user=lytr777@mail.ru main.sh 1
sbatch --cpus-per-task=4 --mem=10G -t 6000 --mail-type=END --mail-user=lytr777@mail.ru main.sh 2
sbatch --cpus-per-task=4 --mem=10G -t 6000 --mail-type=END --mail-user=lytr777@mail.ru main.sh 3
sbatch --cpus-per-task=4 --mem=10G -t 6000 --mail-type=END --mail-user=lytr777@mail.ru main.sh 4
sbatch --cpus-per-task=4 --mem=10G -t 6000 --mail-type=END --mail-user=lytr777@mail.ru main.sh 5
sbatch --cpus-per-task=4 --mem=10G -t 6000 --mail-type=END --mail-user=lytr777@mail.ru main.sh 6
sbatch --cpus-per-task=4 --mem=10G -t 6000 --mail-type=END --mail-user=lytr777@mail.ru main.sh 7
sbatch --cpus-per-task=4 --mem=10G -t 6000 --mail-type=END --mail-user=lytr777@mail.ru main.sh 8

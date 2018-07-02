#!/bin/bash

sbatch --cpus-per-task=32 --mem=30G -t 10000 --mail-type=END --mail-user=lytr777@mail.ru main.sh a0_0
sbatch --cpus-per-task=32 --mem=30G -t 10000 --mail-type=END --mail-user=lytr777@mail.ru main.sh a0_1
sbatch --cpus-per-task=32 --mem=30G -t 10000 --mail-type=END --mail-user=lytr777@mail.ru main.sh a0_2
sbatch --cpus-per-task=32 --mem=30G -t 10000 --mail-type=END --mail-user=lytr777@mail.ru main.sh a0_3
sbatch --cpus-per-task=32 --mem=30G -t 10000 --mail-type=END --mail-user=lytr777@mail.ru main.sh a0_4

#!/bin/bash

sbatch --cpus-per-task=32 --mem=30G -t 240 --mail-type=END --mail-user=lytr777@mail.ru main.sh ev1
sbatch --cpus-per-task=32 --mem=30G -t 240 --mail-type=END --mail-user=lytr777@mail.ru main.sh t1 configurations/tabu.json
sbatch --cpus-per-task=32 --mem=30G -t 480 --mail-type=END --mail-user=lytr777@mail.ru main.sh ev2
sbatch --cpus-per-task=32 --mem=30G -t 480 --mail-type=END --mail-user=lytr777@mail.ru main.sh t2 configurations/tabu.json
sbatch --cpus-per-task=32 --mem=30G -t 720 --mail-type=END --mail-user=lytr777@mail.ru main.sh ev3
sbatch --cpus-per-task=32 --mem=30G -t 720 --mail-type=END --mail-user=lytr777@mail.ru main.sh t3 configurations/tabu.json
sbatch --cpus-per-task=32 --mem=30G -t 1440 --mail-type=END --mail-user=lytr777@mail.ru main.sh ev4
sbatch --cpus-per-task=32 --mem=30G -t 1440 --mail-type=END --mail-user=lytr777@mail.ru main.sh t4 configurations/tabu.json
sbatch --cpus-per-task=32 --mem=30G -t 2880 --mail-type=END --mail-user=lytr777@mail.ru main.sh ev5
sbatch --cpus-per-task=32 --mem=30G -t 2880 --mail-type=END --mail-user=lytr777@mail.ru main.sh t5 configurations/tabu.json

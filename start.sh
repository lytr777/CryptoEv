#!/bin/bash

sbatch --cpus-per-task=32 --mem=30G -t 10000 --mail-type=END --mail-user=lytr777@mail.ru main.sh 11_1 configurations/st_ex/11.json
sbatch --cpus-per-task=32 --mem=30G -t 10000 --mail-type=END --mail-user=lytr777@mail.ru main.sh 12_1 configurations/st_ex/12.json
sbatch --cpus-per-task=32 --mem=30G -t 10000 --mail-type=END --mail-user=lytr777@mail.ru main.sh 15_1 configurations/st_ex/15.json

sbatch --cpus-per-task=32 --mem=30G -t 10000 --mail-type=END --mail-user=lytr777@mail.ru main.sh 11_2 configurations/st_ex/11.json
sbatch --cpus-per-task=32 --mem=30G -t 10000 --mail-type=END --mail-user=lytr777@mail.ru main.sh 12_2 configurations/st_ex/12.json
sbatch --cpus-per-task=32 --mem=30G -t 10000 --mail-type=END --mail-user=lytr777@mail.ru main.sh 15_2 configurations/st_ex/15.json

sbatch --cpus-per-task=32 --mem=30G -t 10000 --mail-type=END --mail-user=lytr777@mail.ru main.sh 11_3 configurations/st_ex/11.json
sbatch --cpus-per-task=32 --mem=30G -t 10000 --mail-type=END --mail-user=lytr777@mail.ru main.sh 12_3 configurations/st_ex/12.json
sbatch --cpus-per-task=32 --mem=30G -t 10000 --mail-type=END --mail-user=lytr777@mail.ru main.sh 15_3 configurations/st_ex/15.json

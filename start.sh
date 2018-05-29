#!/bin/bash

sbatch --cpus-per-task=32 --mem=30G -t 10000 --mail-type=END --mail-user=lytr777@mail.ru main.sh 11a_1 configurations/ad_ex/11.json
sbatch --cpus-per-task=32 --mem=30G -t 10000 --mail-type=END --mail-user=lytr777@mail.ru main.sh 12a_1 configurations/ad_ex/12.json
sbatch --cpus-per-task=32 --mem=30G -t 10000 --mail-type=END --mail-user=lytr777@mail.ru main.sh 15a_1 configurations/ad_ex/15.json

sbatch --cpus-per-task=32 --mem=30G -t 10000 --mail-type=END --mail-user=lytr777@mail.ru main.sh 11a_2 configurations/ad_ex/11.json
sbatch --cpus-per-task=32 --mem=30G -t 10000 --mail-type=END --mail-user=lytr777@mail.ru main.sh 12a_2 configurations/ad_ex/12.json
sbatch --cpus-per-task=32 --mem=30G -t 10000 --mail-type=END --mail-user=lytr777@mail.ru main.sh 15a_2 configurations/ad_ex/15.json

sbatch --cpus-per-task=32 --mem=30G -t 10000 --mail-type=END --mail-user=lytr777@mail.ru main.sh 11a_3 configurations/ad_ex/11.json
sbatch --cpus-per-task=32 --mem=30G -t 10000 --mail-type=END --mail-user=lytr777@mail.ru main.sh 12a_3 configurations/ad_ex/12.json
sbatch --cpus-per-task=32 --mem=30G -t 10000 --mail-type=END --mail-user=lytr777@mail.ru main.sh 15a_3 configurations/ad_ex/15.json

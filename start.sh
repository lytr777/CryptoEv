#!/bin/bash

sbatch --cpus-per-task=32 --mem=30G -t 10000 --mail-type=END --mail-user=lytr777@mail.ru main.sh ap_biv_3

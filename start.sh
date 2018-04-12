#!/bin/bash

sbatch --cpus-per-task=4 --mem=30G -t 1000 --mail-type=END --mail-user=lytr777@mail.ru main.sh 1

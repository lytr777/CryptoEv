#!/bin/bash

sbatch --cpus-per-task=32 --mem=30G -t 8000 --mail-type=END --mail-user=lytr777@mail.ru main.sh 1

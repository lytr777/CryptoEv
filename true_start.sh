#!/bin/bash

sbatch --cpus-per-task=16 --mem=40G -t 4000 --mail-type=END --mail-user=lytr777@mail.ru f_true.sh

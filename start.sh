#!/bin/bash

sbatch --cpus-per-task=32 --mem=30G -t 10000 --mail-type=END --mail-user=lytr777@mail.ru main.sh trivium_test -cp configurations/trivium_64.json -v 3 -d out/debug

#!/bin/bash

sbatch --cpus-per-task=32 --mem=30G --time=24:00:00 --mail-type=END --mail-user=lytr777@mail.ru main.sh -v 3 "$@"

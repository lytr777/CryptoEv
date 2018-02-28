#!/bin/bash

minisat_path="minisat"
mkdir $minisat_path
tar -xf minisat.tar -C $minisat_path --strip-components 1
cd $minisat_path

export MROOT=$PWD
cd core
make rs
cd ../simp
make rs

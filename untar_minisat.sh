#!/bin/bash

name="minisat"
mkdir $name
tar -xf tars/minisat.tar -C $name --strip-components 1
cd $name

export MROOT=$PWD
cd core
make rs
cd ../simp
make rs

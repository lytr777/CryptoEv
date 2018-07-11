#!/bin/bash

name="cryptominisat"
mkdir $name
tar -xf tars/cryptominisat.tar -C $name --strip-components 1
cd $name
mkdir build && cd build
cmake ..
make
make install

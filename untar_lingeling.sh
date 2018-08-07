#!/bin/bash

name="lingeling"
mkdir $name
tar -xf tars/lingeling.tar -C $name --strip-components 1
cd $name
./configure.sh && make

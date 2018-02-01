#!/bin/bash

lingeling_path="lingeling"
mkdir $lingeling_path
tar -xzf lingeling.tar -C $lingeling_path --strip-components 1
cd $lingeling_path
./configure.sh && make

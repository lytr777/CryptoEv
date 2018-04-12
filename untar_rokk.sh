#!/bin/bash

name="rokk"
mkdir $name
tar -xf tars/rokk.tar -C $name --strip-components 1
cd $name

rm -f code/sources/rokk/core/Main.cc
cp ../tools/rokk_re/core/Main.cc code/sources/rokk/core/Main.cc

rm -f code/sources/SatELite/SatELite/Main.C
cp ../tools/SatElite/Main.C code/sources/SatELite/SatELite/Main.C

rm -f code/sources/SatELite/SatELite/Solver_subsume.C
cp ../tools/SatElite/Solver_subsume.C code/sources/SatELite/SatELite/Solver_subsume.C

chmod +x build.sh
./build.sh

cp ../tools/start_rokk.sh binary/rokk_m.sh
cp ../tools/start_rokk.py binary/rokk_py.py

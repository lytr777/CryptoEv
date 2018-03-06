#!/bin/bash

name="rokk"
mkdir $name
tar -xf tars/rokk.tar -C $name --strip-components 1
cd $name

chmod +x build.sh
./build.sh

cp ../tools/start_rokk.sh binary/rokk_m.sh
cp ../tools/start_rokk.py binary/rokk_py.py

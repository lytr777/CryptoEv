#!/bin/bash

name="rokk"
mkdir $name
tar -xf tars/rokk.tar -C $name --strip-components 1
cd $name

chmod +x build.sh
./build.sh

cp ../start_rokk.sh binary/rokk_m.sh

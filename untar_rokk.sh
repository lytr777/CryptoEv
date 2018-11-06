#!/bin/bash

name="rokk"
mkdir $name
tar -xf tars/rokksat.tar -C $name --strip-components 1
cd $name

chmod +x build.sh
./build.sh

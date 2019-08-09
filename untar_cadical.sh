#!/bin/bash

name="cadical"
mkdir $name
tar -xzf tars/cadical-1.0.3.tar.xz -C $name --strip-components 1
cd $name
./configure && make

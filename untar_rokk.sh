#!/bin/bash

name="rokk"
mkdir $name
tar -xf tars/rokk.tar -C $name --strip-components 1
cd $name

./build.sh

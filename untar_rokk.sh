#!/bin/bash

rokk_path="rokk"
mkdir $rokk_path
tar -xf rokk.tar -C $rokk_path --strip-components 1
cd $rokk_path
./build.sh

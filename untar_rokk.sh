#!/bin/bash

rokk_path="rokk"
mkdir $rokk_path
tar -xf rokk.tar -C $rokk_path --strip-components 1

cd $rokk_path/code/sources
cp rokk/core/Makefile core_Make
cp rokk/simp/Makefile simp_Make
rm -rf rokk

mkdir $rokk_path
tar -xf ../../../minisat.tar -C $rokk_path --strip-components 1
rm -f rokk/core/Makefile
rm -f rokk/simp/Makefile
cp core_Make rokk/core/Makefile
cp simp_Make rokk/simp/Makefile

cd ../..
./build.sh

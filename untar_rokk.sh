#!/bin/bash

name="rokk"
mkdir $name
tar -xf tars/rokk.tar -C $name --strip-components 1

cd $name/code/sources
cp rokk/core/Makefile core_Make
cp rokk/simp/Makefile simp_Make
rm -rf rokk

mkdir $name
tar -xf ../../../tars/minisat.tar -C $name --strip-components 1
rm -f rokk/core/Makefile
rm -f rokk/simp/Makefile
cp core_Make rokk/core/Makefile
cp simp_Make rokk/simp/Makefile

cd ../..
./build.sh

#!/bin/bash

name="rokk"
curl -o rokk.tar http://satcompetition.org/edacc/sc14/solver-download/1776
tar -xf rokk.tar -C $name --strip-components 1

cd $name
./build.sh

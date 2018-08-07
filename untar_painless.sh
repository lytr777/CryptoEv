#!/bin/bash

name="painless"
mkdir $name
tar -xzf tars/painless.tar.gz -C $name --strip-components 1
cd $name
make

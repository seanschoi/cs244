#!/bin/bash

# Run with 'sudo ./run.sh fattree 4 1'

export HOME_DIR=$HOME
export NOX_CORE_DIR=$HOME_DIR/noxcore/build/src
export LD_PRELOAD=$NOX_CORE_DIR/nox/coreapps/pyrt/.libs/pyrt.so:$NOX_CORE_DIR/lib/.libs/libnoxcore.so:$NOX_CORE_DIR/builtin/.libs/libbuiltin.so:/usr/lib/libboost_filesystem.so

export NOX_SCRIPT_DIR=`pwd`

echo $NOX_SCRIPT_DIR
./run.py -n $2 -m $1 $1 $3 subspace

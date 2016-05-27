#!/bin/bash

export HOME_DIR=$HOME
export NOX_CORE_DIR=$HOME_DIR/noxcore/build/src
export LD_PRELOAD=$NOX_CORE_DIR/nox/coreapps/pyrt/.libs/pyrt.so:$NOX_CORE_DIR/lib/.libs/libnoxcore.so:$NOX_CORE_DIR/builtin/.libs/libbuiltin.so:/usr/lib/libboost_filesystem.so

./run_unicast.sh
./run_multicast.sh

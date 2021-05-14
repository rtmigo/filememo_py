#!/bin/bash
set -e && source pyrel.sh

# build package, install it into virtual
# environment with pip
pyrel_test_begin

# check, that we can import this module by name
# (so it's installed)
python3 -c "import pickledir"

# remove generated package
pyrel_test_end
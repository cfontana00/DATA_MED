# Common data and routines storage for LaMMA oceanographic modeling team

/modules : shared functions


## TO START:

**set $DIR/modules to your PYTHONPATH in ~/.bashrc**
/bin/bash: line 1: q: command not found

$bash

cd config

cp config_TEMPLATE.json config_MYCONFIG.json
cp variables_mit_TEMPLATE.dat variables_mit_MYCONFYG.dat

cd ../datasets/MY_NEW_DATA

$python3 my_new_routine.py MYCONFIG

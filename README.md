# Common data and routines storage for LaMMA oceanographic modeling team

/modules : shared functions


## TO START:

**set $DIR/modules to your PYTHONPATH in ~/.bashrc**
**export env variable DATA_MED_DIR as /path/to/DATA_MED**

$bash

cd config

cp config_TEMPLATE.json config_MYCONFIG.json
cp variables_mit_TEMPLATE.dat variables_mit_MYCONFYG.dat

cd ../datasets/MY_NEW_DATA

$python3 my_new_routine.py MYCONFIG

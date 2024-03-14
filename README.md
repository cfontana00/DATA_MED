Common data and routines storage for LaMMA oceanographic modeling team

/modules : shared functions


TO START:

set $DIR/modules to your PYTHONPATH in ~/.bashrc

cd config

cp config_TEMPLATE.par config_MYCONFIG.par

cd ../datasets/MY_NEW_DATA

$python3 my_new_routine.py MYCONFIG

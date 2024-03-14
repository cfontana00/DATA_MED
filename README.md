Common data and routines storage for LaMMA oceanographic modeling team

/modules : shared functions


TO START:

cd config

cp config_TEMPLATE.par config_MYCONFIG.par

cd ../MY_NEW_DATA
echo config_MYCONFIG.par >> .gitignore

$MY_NEW_DATA/my_new_routine.py MYCONFIG

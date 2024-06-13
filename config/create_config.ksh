#!/bin/ksh


if [ -f config_$1.json ];then
  echo "Warning, configuration $1 exists"
  echo "Proceed ?"
  echo "Press any key to continue or abort ..."
  read -s -n 1 any_key
fi



cp config_TEMPLATE.json config_$1.json
cp variables_mit_TEMPLATE.dat variables_mit_$1.dat
cp cmems_TEMPLATE.dat cmems_$1.dat

echo ''
echo "Configuration $1 created"

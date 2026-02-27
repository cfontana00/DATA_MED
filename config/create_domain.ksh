#!/bin/ksh


for domain in NAD GOT GSN ION LIG NAD SAD SAR SIC TYR ISO;do

lower=`echo "$domain" | awk '{print tolower($0)}'`
echo $lower
cat config_DOMAIN.json | sed -e s/LOWER/$lower/  | \
                         sed -e s/DOMAIN/$domain/  \
> config_$domain.json

done

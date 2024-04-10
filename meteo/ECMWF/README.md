## Reference for conversion to specific humidity

Td=d2m-273.15; % K to deg C

p=msl./100; % Pa to mb

e = 6.112.*exp((17.67.*Td)./(Td + 243.5));

q = (0.622 .* e)./(p - (0.378 .* e));

https://www.eol.ucar.edu/projects/ceop/dm/documents/refdata_report/eqns.html

(Bolton 1980)
where:

   e = vapor pressure in mb;

   Td = dew point in deg C;

   p = surface pressure in mb;

   q = specific humidity in kg/kg.

(Note the final specific humidity units are in g/kg = (kg/kg)*1000.0)

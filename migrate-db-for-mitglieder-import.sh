#/bin/bash
#

psql -U postgres -d spsv -f ../dumps/2024-05-14-rheinfelden-django-5.pgdump

./manage.py migrate

psql -U postgres -d spsv <<EOF
update sasse_sektion set name='SPSV', nummer='1.02.00' where id=0;
update sasse_sektion set nummer='1.02.00.001' where id=1;
update sasse_sektion set nummer='1.02.00.002' where id=2;
update sasse_sektion set nummer='1.02.00.003' where id=3;
update sasse_sektion set nummer='1.02.00.004' where id=4;
update sasse_sektion set nummer='1.02.00.005' where id=5;
update sasse_sektion set nummer='1.02.00.007' where id=7;
update sasse_sektion set nummer='1.02.00.008' where id=8;
update sasse_sektion set nummer='1.02.00.010' where id=10;
update sasse_sektion set nummer='1.02.00.011' where id=11;
update sasse_sektion set nummer='1.02.00.012' where id=12;
update sasse_sektion set nummer='1.02.00.013' where id=13;
update sasse_sektion set nummer='1.02.00.014' where id=14;
update sasse_sektion set nummer='1.02.00.015' where id=15;
update sasse_sektion set nummer='1.02.00.016' where id=16;
update sasse_sektion set nummer='1.02.00.017' where id=17;
update sasse_sektion set nummer='1.02.00.018' where id=18;
update sasse_sektion set nummer='1.02.00.019' where id=19;
update sasse_sektion set nummer='1.02.00.020' where id=20;
update sasse_sektion set nummer='1.02.00.021' where id=21;
update sasse_sektion set nummer='1.02.00.022' where id=22;
update sasse_sektion set nummer='1.02.00.023' where id=23;
update sasse_sektion set nummer='1.02.00.024' where id=24;
update sasse_sektion set nummer='1.02.00.025' where id=25;
update sasse_sektion set nummer='1.02.00.026' where id=26;
update sasse_sektion set nummer='1.02.00.027' where id=27;
update sasse_sektion set nummer='1.02.00.028' where id=28;
update sasse_sektion set nummer='1.02.00.029' where id=29;
update sasse_sektion set nummer='1.02.00.030' where id=30;
update sasse_sektion set nummer='1.02.00.031' where id=31;
update sasse_sektion set nummer='1.02.00.032' where id=32;
update sasse_sektion set nummer='1.02.00.033' where id=33;
update sasse_sektion set nummer='1.02.00.034' where id=34;
update sasse_sektion set nummer='1.02.00.035' where id=35;
update sasse_sektion set nummer='1.02.00.036' where id=36;
update sasse_sektion set nummer='1.02.00.037' where id=37;
update sasse_sektion set nummer='1.02.00.038' where id=38;
update sasse_sektion set nummer='1.02.00.039' where id=39;
update sasse_sektion set nummer='1.02.00.040' where id=40;
update sasse_sektion set nummer='1.02.00.041' where id=41;
update sasse_sektion set nummer='1.02.00.042' where id=42;

update sasse_sektion set nummer='W07' where id=43;
update sasse_sektion set nummer='W08' where id=44;
update sasse_sektion set nummer='W09', name='AC Matte Bern' where id=47;
update sasse_sektion set nummer='W13' where id=48;
update sasse_sektion set nummer='W14', name='WSC Bern' where id=49;
update sasse_sektion set nummer='W06' where id=50;
EOF

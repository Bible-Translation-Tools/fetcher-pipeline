#!/bin/bash

cd /fetcher-pipeline || exit

pm2 start "python3.8 app.py -i /home/vsftpd/ -t -v -hr 0 -mn 0" --name fetcher-pipeline

/usr/sbin/run-vsftpd.sh
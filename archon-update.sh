#!/bin/bash

echo "Archon updater"

echo "Stopping archon-server service"
systemctl stop archon-server

WORKINGDIR="$(pwd "$0")"
APPCONFIG="config/app.yaml"
APICONFIG="config/api.yaml"
SMTPCONFIG="config/smtp.yaml"
STORAGEDIR="storage"

ARCHONDIR="/opt/archon-server"
ARCHONDIRBACKUP="/opt/t0-archon-server"

echo "WORKINGDIR: $WORKINGDIR"

if [[ "$WORKINGDIR" == "$ARCHONDIR" ]];
then
    echo "Can not run in $WORKINGDIR, copy this script somewhere else, e.g. /opt"
    exit 1
fi

if [[ -d $ARCHONDIRBACKUP ]];
then
    echo "Directory $ARCHONDIRBACKUP exists, deleting"
    rm -rf $ARCHONDIRBACKUP
fi

if [[ -d $ARCHONDIR ]];
then
    echo "Directory $ARCHONDIR exists"
    echo "Backup directory $ARCHONDIR to $ARCHONDIRBACKUP"
    mv $ARCHONDIR $ARCHONDIRBACKUP
else
    echo "Directory $ARCHONDIR not found"
fi

cd /opt
git clone https://github.com/prochor666/archon-server.git

cp -f $ARCHONDIRBACKUP/$APPCONFIG $ARCHONDIR/$APPCONFIG
cp -f $ARCHONDIRBACKUP/$APICONFIG $ARCHONDIR/$APICONFIG
cp -f $ARCHONDIRBACKUP/$SMTPCONFIG $ARCHONDIR/$SMTPCONFIG
cp -r $ARCHONDIRBACKUP/$STORAGEDIR $ARCHONDIR

echo "Running install script"
chmod +x $ARCHONDIR/install
cd $ARCHONDIR
./install
cd /opt

echo "Starting archon-server service"
systemctl start archon-server
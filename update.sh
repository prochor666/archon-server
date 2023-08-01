#!/bin/bash

echo "dirname : [$(dirname "$0")]"

echo "Archon updater"

APPCONFIG="config/app.yaml"
SAPPCONFIG="config/sample.app.yaml"
APICONFIG="config/api.yaml"
SAPICONFIG="config/sample.api.yaml"
SMTPCONFIG="config/smtp.yaml"
SSMTPCONFIG="config/sample.smtp.yaml"
SITESDIR="storage/sites"
DEVICESDIR="storage/devices"
RESOURCESDIR="storage/resources"
LOGSDIR="storage/logs"

ARCHONDIR="/opt/archon-server"
ARCHONDIRBACKUP="/opt/t0-archon-server"

t0-archon-server
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

cp $ARCHONDIRBACKUP/$APPCONFIG $ARCHONDIR/$APPCONFIG
cp $ARCHONDIRBACKUP/$APICONFIG $ARCHONDIR/$APICONFIG
cp $ARCHONDIRBACKUP/$SMTPCONFIG $ARCHONDIR/$SMTPCONFIG
cp $ARCHONDIRBACKUP/$SITESDIR $ARCHONDIR/$SITESDIR
cp $ARCHONDIRBACKUP/$DEVICESDIR $ARCHONDIR/$DEVICESDIR
cp $ARCHONDIRBACKUP/$RESOURCESDIR $ARCHONDIR/$RESOURCESDIR
cp $ARCHONDIRBACKUP/$LOGSDIR $ARCHONDIR/$LOGSDIR


def monitor_service_config() -> str:

    config = '''#!/bin/bash
#
# @author prochor666@gmail.com
#
# Control monitoring service installer

SERVICE_FILE="/etc/systemd/system/archon-monitor-collector.service"

if [[ ! -f "${SERVICE_FILE}" ]];
then

echo "
[Unit]
Description=Control monitor data collector

[Service]
ExecStart=/opt/archon/monitor/archon-monitor.sh

[Install]
WantedBy=multi-user.target
" > ${SERVICE_FILE}

systemctl daemon-reload

systemctl enable archon-monitor-collector.service
systemctl start archon-monitor-collector.service
fi

systemctl stop archon-monitor-collector.service
sleep 2
systemctl start archon-monitor-collector.service
'''

    return config


def monitor_service_script() -> str:

    script = '''#!/bin/bash
#
# @author prochor666@gmail.com
#
# Control resource monitoring

LOG_DIR="/opt/archon/stats"
LOG_FILE_TMP="monitor.tmp"
LOG_FILE="archon-monitor.data"
SITE_ROOT="/var/www/html"
SNAPSHOT_INTERVAL=10

if [[ ! -d "${LOG_DIR}" ]];
then
    mkdir -p "${LOG_DIR}"
fi

# Logging
exec > >(tee -a ${LOG_DIR}/${LOG_FILE_TMP}) 2>&1

function cpu()
{
    echo "<control-monitor-cpu>"
    echo "$(cat /proc/cpuinfo)"
    echo "</control-monitor-cpu>"
}

function cpu_load()
{
    echo "<control-monitor-stat-sample${@}>"
    echo "$(cat /proc/stat)"
    echo "</control-monitor-stat-sample${@}>"
}

function memory()
{
    echo "<control-monitor-memory>"
    echo "$(cat /proc/meminfo)"
    echo "</control-monitor-memory>"
}

function storage()
{
    echo "<control-monitor-storage>"
    echo "$(df -P /var/www)"
    echo "</control-monitor-storage>"
}

function network()
{
    echo "<control-monitor-network${@}>"
    echo "$(cat /proc/net/dev)"
    echo "</control-monitor-network${@}>"
}

function setLastUpdateUTC() {
    echo "<control-monitor-last-update>"
    echo $(date -u -d @$(date +%s) +"%Y-%m-%d-%H-%M-%S")
    echo "</control-monitor-last-update>"
}

function network_totals()
{
    echo "<control-monitor-network-stats>"

    # Scan network devices
    for DEVICE in $(ls -I "lo" /sys/class/net);
    do
        STATEFILE="/sys/class/net/${DEVICE}/operstate"
        if [[ -f ${STATEFILE} ]];
        then
            STATE="$(cat ${STATEFILE})"
            if [[ "${STATE}" == "up" ]];
            then
                # Device is up, read some data
                RXBYTESFILE="/sys/class/net/${DEVICE}/statistics/rx_bytes"
                TXBYTESFILE="/sys/class/net/${DEVICE}/statistics/tx_bytes"
                echo "Device: ${DEVICE}"

                if [[ -f ${RXBYTESFILE} ]];
                then
                    echo "RX: $(cat ${RXBYTESFILE})"
                fi

                if [[ -f ${TXBYTESFILE} ]];
                then
                    echo "TX: $(cat ${TXBYTESFILE})"
                fi
            fi
        fi
    done

    echo "</control-monitor-network-stats>"
}


# Infinite work
while true
do
    echo "" > "${LOG_DIR}/${LOG_FILE_TMP}"
    echo "SSH server hostname: $(hostname)"
    cpu
    cpu_load 1
    sleep 2
    cpu_load 2
    memory
    storage
    network 1
    sleep 1
    network 2
    network_totals
    setLastUpdateUTC
    cp ${LOG_DIR}/${LOG_FILE_TMP} ${LOG_DIR}/${LOG_FILE}
    cp ${LOG_DIR}/${LOG_FILE_TMP} ${SITE_ROOT}/${LOG_FILE}
    sleep ${SNAPSHOT_INTERVAL}
done
'''

    return script


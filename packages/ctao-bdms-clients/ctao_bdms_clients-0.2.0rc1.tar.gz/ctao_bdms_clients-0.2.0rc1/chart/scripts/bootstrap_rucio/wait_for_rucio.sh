while true; do
    openssl s_client -connect ${HELM_RELEASE_NAME:?}-rucio-server:443 && break
    sleep 3
done

echo "Rucio server is responding on port 443"

if [ -z "$WAIT_RUCIO_PING" ]; then
    echo "Skipping rucio ping check"
else
    while true; do
        rucio ping && break
        sleep 3
    done

    echo "Rucio server is responding to ping"
fi

ls -l /opt/rucio/etc/
cat /opt/rucio/etc/rucio.cfg

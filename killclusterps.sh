#!/bin/bash
if [ -z $1 ]; then
    echo "No host file given"
    exit 1
fi

# $1 should be a file of hosts to ssh to
while IFS='' read -r host || [[ -n "$host" ]]; do
    echo "Host: $host"
    # ssh $host /bin/bash <<EOF 
    #     cd $HeavyVechicle
    #     kill -9 $(pgrep -u brandtr python3)
    ssh -tt $host "cd $HeavyVechicle; kill $(pgrep -u brandtr python3)" &
# EOF
done < "$1"

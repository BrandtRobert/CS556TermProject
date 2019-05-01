#!/bin/bash
if [ -z $1 ]; then
    echo "No host file given"
    exit 1
fi

# $1 should be a file of hosts to ssh to
while IFS='' read -r host || [[ -n "$host" ]]; do
    echo "Host: $host"
    ssh -tt $host "cd $HeavyVechicle; nohup ./bashrunner.sh" &
done < "$1"

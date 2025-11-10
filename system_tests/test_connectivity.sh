#!/bin/bash
test_connectivity()
{
    CONTAINER_NAME=$1
    DESTINATION=$2
    REQUIRED_MAX_RTT=$3

    parent_path=$( cd "$( dirname "${BASH_SOURCE[0]}" )"; pwd -P )
    aliases_path=$parent_path/../aliases-scripts

    bash $aliases_path/up.sh
    timeout 15s python3 $parent_path/../router/main.py &
    sleep 3 # Letting the router load
    MAX_RTT=$( docker exec -t $CONTAINER_NAME sh -c "ping -c 5 $DESTINATION" | grep "= "| cut -d ' ' -f 4 | cut -d '/' -f 3 )
    bash $aliases_path/down.sh
    if [ -z "$MAX_RTT" ]; then
        echo "No Connectivity"
    elif [ -n "$REQUIRED_MAX_RTT" ] && [ $(echo "$MAX_RTT > $REQUIRED_MAX_RTT" | bc) -eq 1 ]; then
        echo "Connectivity is too slow:"
        echo "max RTT is $MAX_RTT"
    else
        echo "Connectivity is valid:"
        echo "max RTT is $MAX_RTT"
        return 0
    fi
    return 1
}

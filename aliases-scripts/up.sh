#!/bin/bash


# --- styling ---
GREEN='\033[32m'
NC='\033[0m'

# --- paths ---
current_path=$(pwd - P)
parent_path=$( cd "$( dirname "${BASH_SOURCE[0]}" )"; pwd -P )

printf "${GREEN}[+] Starting lab environment...${NC}\n"
cd $parent_path/../docker
docker compose up -d

printf "${GREEN}[+] Configuring host kernel/networking for router simulation...${NC}\n"

# Disable kernel ARP handling on router (and containers) interfaces — the Python router manages ARP instead
printf "\t- Disabling ARP on c1_iface,c2_iface...\n"
sudo ip link set dev c1_iface arp off
sudo ip link set dev c2_iface arp off

# Disable kernel ICMP Echo Replies so only the router answers pings.
printf "\t- Disabling kernel ICMP Echo Replies...\n"
sudo sysctl net.ipv4.icmp_echo_ignore_all=1 > /dev/null

# Disable kernel IPv4 forwarding so only the router handles packet routing.
printf "\t- Disabling kernel IP forwarding...\n"
sudo sysctl net.ipv4.ip_forward=0 > /dev/null

# Remove pre-routing iptables configuration Docker made to our bridge networks.
# This is redundant if your Docker daemon is configured with { "iptables": false }
printf "\t- Cleaning up iptables raw table PREROUTING rules for c1_iface and c2_iface (if any)...\n"
sudo iptables -t raw -L PREROUTING -v --line-numbers  \
    | grep -E 'c1_iface|c2_iface' \
    | awk '{print $1}' \
    | sort -rn \
    | xargs -r -I{} sudo iptables -t raw -D PREROUTING {}

printf "${GREEN}[v] Lab environment started and host networking configured.${NC}\n"

cd $current_path

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

printf "${GREEN}[v] Lab environment started and host networking configured.${NC}\n"

cd $current_path

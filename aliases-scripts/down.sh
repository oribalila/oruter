#!/bin/bash

# --- styling ---
CYAN='\033[36m'
NC='\033[0m'

# --- paths ---
current_path=$(pwd - P)
parent_path=$( cd "$( dirname "${BASH_SOURCE[0]}" )"; pwd -P )

printf "${CYAN}[x] Shutting down lab environment...${NC}\n"
cd $parent_path/../docker
docker compose down

printf "${CYAN}[x] Deconfiguring host kernel/networking for router simulation...${NC}\n"
# No need to restore ARP or iptables rules for c1_iface/c2_iface —
# docker compose down removes the interfaces and related configuration.

# Restore ICMP responses
printf "\t- Enabling kernel ICMP Echo Replies...\n"
sudo sysctl net.ipv4.icmp_echo_ignore_all=0 > /dev/null

# Restore IPv4 forwarding
printf "\t- Enabling kernel IP forwarding...\n"
sudo sysctl net.ipv4.ip_forward=1 > /dev/null

printf "${CYAN}[x] Lab environment stopped and host networking deconfigured.${NC}\n"

cd $current_path

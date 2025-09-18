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

printf "${GREEN}[v] Lab environment started and host networking configured.${NC}\n"

cd $current_path

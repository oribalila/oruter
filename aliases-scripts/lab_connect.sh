#!/bin/bash
lab_connect()
{
    command docker exec -it $@ sh
}

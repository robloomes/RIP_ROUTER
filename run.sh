#!/bin/sh
#Need to give execute permission to file to acheive runtime e.g chmod +x run.sh

python routing_daemon.py config7.txt&
gnome-terminal -e "python routing_daemon.py config2.txt"
gnome-terminal -e "python routing_daemon.py config3.txt"
gnome-terminal -e "python routing_daemon.py config4.txt"
gnome-terminal -e "python routing_daemon.py config5.txt"
gnome-terminal -e "python routing_daemon.py config6.txt"
gnome-terminal -e "python routing_daemon.py config1.txt"

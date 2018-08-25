""" *******************************************************
routing_daemon
COSC364 RIP assignment
Authors: Robert Loomes, Angela Vo
Usercode: rwl29, atv13

Purpose: This program will create a single instance
of a Linux RIP routing daemon. It takes a seperate
config file as a parameter that has needed ID and
port number information.
**********************************************************
"""

import socket
import sys
import select
import input_parser
from router import Router
import struct
from threading import Timer


def signal_handler(signal, frame):
    sys.exit()

def main(argv):
    """Main function of routing_daemon"""

    # Checks that there are the correct number of inputs
    if len(sys.argv) > 2:
        print("ERROR: Too many arguments given. Only 1 config file is required.")
        sys.exit()
    elif len(sys.argv) < 2:
        print("ERROR: No config file given")
        sys.exit()

    # There is the correct number of inputs - move to check the file itself
    else:

        info_dict = input_parser.read_config(sys.argv[1])
        router_instance = Router(info_dict)
        input_sockets = router_instance.udp_sockets # list of router's input sockets

        print(
        "You are running file: {}\nRouter ID: {}\nInput ports: {}\nNeighbours (port, metric, id): {}".\
        format(argv[1], router_instance.router_id,
        router_instance.input_ports, router_instance.output_ports))

        first_thread = Timer(10.0, router_instance.send_table) # send first update
        first_thread.daemon = True
        first_thread.start()

        # infinite loop where we wait for input
        while True:
            # select blocks while waiting for events/ inputs
            read_sockets, write_sockets, error_sockets = \
            select.select(input_sockets, [], [])

            #read_sockets is now a list of input sockets that have
            #updates i.e. routing tables from other routers ready to be read
            for update in read_sockets:
                read_sockets.remove(update)
                routing_table, sender_addr = update.recvfrom(1024)
                router_instance.update_table(routing_table, sender_addr[1])



if __name__ == "__main__":
    main(sys.argv)

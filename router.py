""" *******************************************************
router class
COSC364 RIP assignment
Authors: Robert Loomes, Angela Vo
Usercode: rwl29, atv13

Purpose: This defines the class for each router
**********************************************************
"""
import socket
import sys
import select
import input_parser
import time
from threading import Timer
import struct
import random

class Router:

    def __init__(self, info_dict):

        self.router_id = info_dict["router_id"]
        self.input_ports = info_dict["input_ports"]
        self.output_ports = info_dict["output_ports"]
        self.periodic = info_dict["periodic"]
        self.timeout = info_dict["timeout"]
        self.garbage = info_dict["garbage"]
        self.udp_sockets = []
        self.router_table = {}
        self.timeout_timers = {}
        self.garbage_timers = {}

        for port in self.input_ports:
            socket = self.create_bind_socket(port)
            self.udp_sockets.append(socket)

        self.sender_socket = self.udp_sockets[0]

        for port in self.output_ports:
            self.timeout_timers[port['router_id']] = Timer(self.timeout, self.timeout_neighbour, [-1])

    def refresh_timeout_timer(self, source):
        try:
            self.timeout_timers[source].cancel()  #if timer already exists for this route, cancel it.
        except KeyError:
            pass

        self.timeout_timers[source] = Timer(self.timeout, self.timeout_neighbour, [source])
        self.timeout_timers[source].start()

    def timeout_neighbour(self, source):
        self.router_table[source]['metric'] = 16 #announces route as unreachable
        self.refresh_garbage_timer(source)    #starts garbage timer

    def refresh_garbage_timer(self, source):
        self.garbage_timers[source] = Timer(self.garbage, self.delete_route, [source])
        self.garbage_timers[source].start()

    def delete_route(self, source):
        if (self.router_table[source]['metric'] == 16) and (source in self.router_table):
            self.router_table.pop(source, None) #remove route from router table

        for i, d in enumerate(self.output_ports): #remove route from neighbour list
            if d['router_id'] == 1:
                self.output_ports.pop(i)

    def create_bind_socket(self,port):
        try:
            udp_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            udp_sock.bind(('localhost', port))
            return udp_sock

        except socket.error as msg:
            print("ERROR: Your socket cannot be created\nERROR CODE: {}\nERROR MSG: {}"
            .format(msg[0], msg[1]))
            sys.exit()

    def encode_table(self,neighbour):

        output_table = [2, 2, self.router_id, self.router_id, neighbour["metric"]]

        # SPLIT HORIZON
        for destination in self.router_table:
            if not self.router_table[destination]["next_hop"] == neighbour["router_id"]: #our destination's next hop is not our sender
                output_table.append(destination),
                output_table.append(self.router_table[destination]["metric"])
        s = struct.Struct('bbh{}h'.format(len(output_table) - 3))
        table = s.pack(*output_table)
        return table



    def decode_table(self, routing_update):
        decode_format = 'bbh'+'{}h'.format((len(routing_update) - 4)/2);
        # print(decode_format);
        data = struct.unpack(decode_format, routing_update)
        # print(data)
        return_table = {
            "command":data[0],
            "version":data[1],
            "source":data[2],
            "routes": []
        }
        for i in range(3, len(data) -1, 2):
            return_table["routes"].append({
                "destination":data[i],
                "metric":data[i + 1]
            })

        return return_table


    def send_table(self):

        timer_var = random.uniform(-(0.2*self.periodic), 0.2*self.periodic) #600 milliseconds = 20% variance on a 3 second timer
        sender_socket = self.udp_sockets[0]
        for neighbour in self.output_ports:
            sender_socket.sendto(self.encode_table(neighbour), ('localhost', neighbour["port"]))
            print("Sending to neighbour: {}, sending: {}".format(neighbour["router_id"], self.decode_table(self.encode_table(neighbour))))
        Timer(self.periodic+timer_var, self.send_table).start()



    def update_table(self, routing_update, sender_port):

        decoded_table = self.decode_table(routing_update)
        command = decoded_table["command"]
        version = decoded_table["version"]
        source = decoded_table["source"]
        rte_update = decoded_table["routes"]
        source_info = list(filter(lambda rte: rte["destination"] == source, rte_update))
        # header info wrong
        # CHECK METRIC IN THE RIGHT RANGE
        if (command != 2) or (version != 2) or (source not in list(map(lambda output: output["router_id"], self.output_ports))):
            print("ERROR: incorrect packet received, packet dropped")

        # if we have the sender's info, but it's not already in the router_table
        elif len(source_info) == 1 and not source in self.router_table:
            destination = source_info[0]["destination"]
            metric = source_info[0]["metric"]
            if metric >= 16:
                print("ERROR: packet reached maximum hops, packet dropped")
            else:
                self.router_table[destination] = {"next_hop": destination, "port": sender_port, "metric": metric}


        elif source in self.router_table:
            for entry in rte_update:
                destination = entry["destination"]
                metric = entry["metric"]

                # logic - if route in table, must be updated. If this is a new route and it is at a cost of 16 - drop it. 
                # if metric is greater than 16
                if metric > 16:
                    print("ERROR: packet reached maximum hops, packet dropped")
                # if metric is 16 then update our table accordingly
                elif (metric == 16) and (destination in self.router_table):
                    self.router_table[destination]["metric"] = 16
                    if (destination in self.garbage_timers) and (self.garbage_timers[destination].is_alive() == False):
                        self.refresh_garbage_timer(destination)
                # if metric is less than 16
                else:
                    if not destination in self.router_table:
                        # if metric.self + metic > 16 - update the table send out triggered update
                        self.router_table[destination] = {"next_hop": source, "port": sender_port, "metric": self.router_table[source]["metric"] + metric}
                    else:
                        # if metric.self + metic > 16 - update the table send out triggered update
                        if(self.router_table[destination]["metric"] > self.router_table[source]["metric"] + metric):
                            self.router_table[destination]["metric"] = self.router_table[source]["metric"] + metric
                            self.router_table[destination]["next_hop"] = source
                            self.router_table[destination]["port"] = sender_port
                    if not self.router_table[destination] in self.output_ports:
                        self.refresh_timeout_timer(entry["destination"]) #starts timeout for route in update

        self.refresh_timeout_timer(source) #starts timeout for neighbour that supplied the update

        print(self.router_table)

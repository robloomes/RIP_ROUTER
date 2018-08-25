""" *******************************************************
input parser
COSC364 RIP assignment
Authors: Robert Loomes, Angela Vo
Usercode: rwl29, atv13

Purpose: This program will scrub and check input to
ensure the config file is correct
**********************************************************
"""
import sys
import os

def parse_num(s):
	try:
		return int(s)
	except ValueError:
		return -1

def check_router_id(id_value):
	if (id_value < 1) or (id_value > 64000):
		return -1
	else:
		return id_value

def check_port_num(num):
	if (num < 1024) or (num > 64000):
		return -1
	else:
		return num

def check_metric(metric):
	if (metric < 1) or (metric > 16):
		return -1
	else:
		return metric

def read_config(file_name):
	"""Reads lines from a file and stores them in a list.
	Strips trailing whitespace and returns a dictionary with the input info
	If the config file is malformed we exit Python with an error message
	"""

	if not os.path.isfile(file_name):
		sys.exit("ERROR: Your config file cannot be found")

	else:
		config_input = {
		"router_id": -1,
		"input_ports": [],
		"output_ports": [],
		"periodic": 3,
		"timeout": 18,
		"garbage": 12,
		}

		with open(file_name) as file: # this ensures the file is closed
			config_lines = [line.strip() for line in file]

		for item in config_lines:
			config_values = item.split(" ", 1); # split off the name of each input line

			if (config_values[0] == "router-id"):
				config_input["router_id"] = parse_num(config_values[1:][0].strip())
				if check_router_id(config_input["router_id"]) == -1:
					sys.exit("ERROR: Your router ID is invalid")

			elif config_values[0] ==  "input-ports":
				for item in config_values[1:][0].split(','):
					input_val = parse_num(item)
					if (check_port_num(input_val) == -1) or (input_val in config_input["input_ports"]):
						sys.exit("ERROR: Your input-ports are invalid")
					else:
						config_input["input_ports"].append(input_val)

			elif config_values[0] ==  "output-ports":
				current_output_ports = []
				current_router_id = []

				for output in config_values[1:][0].split(','):
					neighbour = output.split('-') # a list that has each ['port num', 'metric value', 'routerid']
					if (len(neighbour) != 3):
						sys.exit("ERROR: Your output-ports are invalid")
					else:
						for i in range(0,len(neighbour)):
							value = parse_num(neighbour[i])
							if (value == -1):
								sys.exit("ERROR: Your output-ports are invalid")
							else:
								neighbour[i] = value

						# add the output ports and router ids to a list to
						# find duplicates
						current_output_ports.append(neighbour[0])
						current_router_id.append(neighbour[2])

						if (check_port_num(neighbour[0]) == -1 or
							check_metric(neighbour[1]) == -1 or
							check_router_id(neighbour[2]) == -1):
							sys.exit("ERROR: Your output-ports are invalid")

					config_input["output_ports"].append({"port":neighbour[0], "metric":neighbour[1], "router_id": neighbour[2]})

				# check to see if there are duplicate router ids or output ports
				if ((len(current_router_id) != len(set(current_router_id))) or
					(len(current_output_ports) != len(set(current_output_ports)))):
					sys.exit("ERROR: Your router-id and/or output-ports are not unique")

			elif config_values[0] == "periodic":
				config_input["periodic"] = parse_num(config_values[1:][0].strip())
				if (config_input["periodic"] == -1):
					sys.exit("ERROR: Your periodic timer is invalid")

			elif config_values[0] == "timeout":
				config_input["timeout"] = parse_num(config_values[1:][0].strip())
				if (config_input["timeout"] == -1):
					sys.exit("ERROR: Your timeout value is invalid")

			elif config_values[0] == "garbage":
				config_input["garbage"] = parse_num(config_values[1:][0].strip())
				if (config_input["garbage"] == -1):
					sys.exit("ERROR: Your garbage-collection time is invalid")

			else:
				sys.exit("ERROR: Your config file is malformed")

		if (len(config_input["input_ports"]) == 0 or
			len(config_input["output_ports"]) == 0 or
			config_input["router_id"] == -1 or
			int(config_input["timeout"]/config_input["periodic"]) != 6 or
			int(config_input["garbage"]/ config_input["periodic"]) != 4):
			sys.exit("ERROR: Your config file is malformed")

		return config_input

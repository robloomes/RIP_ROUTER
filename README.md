Successes
---------
Our program complies with the RIPv2 specification outlined in the RFC 2453. Specifically it successfully does the following:
    -Each router obtains optimal routes regardless of the order of router startup or the time delay between each one. 
    -The network as a whole converges quickly.
    -We utilised a checksum in our packets to ensure that no corrupted packets would be processed by a router. 
    -When a router fails, the network recalculates optimal routes quickly, and when the router comes back up, it will              recalculate again.
    -Our implementation minimises the likelihood of routing loops and the count to infinity issue using split horizon with        poison reverse. An example of our split horizon and poison reverse used in our program is as follows (using the network      given in assignment outline): 
     SPLIT HORIZON: If router 1 gets to router 3 using router 2 as the next hop, router 1 does not include  3 as an entry in      the routing update it sends to 2, as this could lead to a routing loop if the link between router 2 and router 3 goes        down. Similarly, it also does not include router 4 in the routing update as router 1 uses router 2 as the next hop to        get to router 4.
     POISON REVERSE: If router 1 gets an update from router 7 informing it that router 4 is unreachable, router 1 will send a      triggered update to router 6, 2 AND 7 informing them that router 4 is unreachable. This way, router 7 knows that it          cannot get to router 4 via router 1. 

Areas of Improvement
--------------------
Scalability of the network is called into question when implementing multi-threading techniques in regards to CPU and memory loads. Our current network configuration uses a low amount of resources, but if we implemented hundreds (thousands?) more routers into our network, it is not known how this would perform compared to some other non-threaded implementations of RIP. 

Atomicity of Event Processing
-----------------------------
In our program, we essentially three main processes that run at the same time:
Sending updates
Receiving updates
Updating our own routing tables given the updates we have received

Each of these events are isolated from one another, with no one event being interrupted by another. This is achieved by making use of the “threading.Timer” library, where each time a timer thread is created, it works in parallel to any other existing threads. 

Our send_table() function continuously calls itself using the Timer function and executes in parallel without being called by any other functions. In this instance, atomicity is achieved as there is no possible event that could cause the interruption of the cycle. Similarly, the timeout and garbage timers are handled by additional threads. Once the threads have begun, these timers are unaffected by any processing times of the send/receive packet functions. 

Lastly, to ensure that we do not send our routing table before we have finished updating it (because we don’t want to propogate incorrect information), we set a “updating_table” flag to True while we’re updating our table and to False once we’re done; our send table function will only send the routing table once this flag is set to False. This also applies to triggered updates. 

Changing Timer Values of Routers
--------------------------------
In changing the timer values of routers we expected our network to still converge correctly, but a little bit slower.

In our testing, we looked at changing Router 1’s timers to double what the default value is for each - periodic went from 3 seconds to 6 seconds, the timeout timer went from 18 to 36 and the garbage timer from 12 to 24. 

Our start up convergence didn’t take too long compared to what it was at the default values. 
However, when Router 2 went down, it took a relatively long time for all routers to remove Router 2 from their routing tables. This is because Router 1 waited twice as long to realise that Router 2 had gone down compared to all other routers and kept sending out updates every 6 seconds telling it’s neighbours that 2 was still alive (and for a brief moment, some routers believed it and rerouted to 2 via 1). Eventually though, all routers converged correctly and removed 2 from their tables. 

Malforming the Configuration File/ Bash Input
---------------------------------------------
Given our creation of an input parser, we expected that if there was any error in the configuration file or the terminal line input, we would see an error message and the program would not even start. 

To test, we malformed the configuration files in many ways, including:
    Adding duplicates of input ports, output ports and router-id
        Error message: “Your router-id and/or output-ports are not unique” and “Your input-ports are invalid”
    Having port numbers outside the acceptable range
        Error message: “Your input-ports are invalid” and “Your output-ports are invalid”
    Changing the timers so the ratio of timeout to garbage to periodic update was wrong
        Error message: “Your config file is malformed”
    Having strings where we expected integers
        Error message: “Your config file is malformed”
    Adding in junk lines in the file
        Error message: “Your config file is malformed”

We also attempted to run the program with a non-existent configuration file, more than one parameter in the terminal line and zero parameters in the terminal line. The error messages we expected back respectively were: “Your config file cannot be found”, “Too many arguments given. Only 1 config file is required” and “No config file given”.

The results across all tests came back with the expected error messages. 








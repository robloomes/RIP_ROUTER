1) create 7 separate config files- donezo
2) create python program to test config files
3) create router using each config file

***Router port number naming conventions***
All port numbers are 4 digit numbers, representing either an input or output number.
Input numbers: The first 2 digits are the same as the ID number for that router. The 3rd digit is always a 0 placeholder. The 4th digit is the same as the -expected- ID number of the router it is linking to.
Output numbers: The first 2 digits are the same as the -expected- ID number for the router it is linking to. The 3rd digit is always a 0 placeholder. The 4th digit is the same as the ID number for the router.
NOTE: as the routing topography changes with the exclusion/inclusion of more routers, these naming conventions may no longer be relevant. E.g an output port no. of 2201 at router ID-1 may no longer be linking to router ID-2, as that router is no longer operational, and is excluded from the initial network topography.

TODO

script for running 7 instances.

Create timers for each routing entry upon routing update received:
Enable functionality for routing table updates when another routing instance is removed
-Triggered updates- with poison reverse
-Timeout timer-
-Garbage timer-
Timer periodic offsets +/- 20%. Import math library.
Checksum for routing???? maybe
implement a loop counter to keep track of how many updates each router has sent out??
implement max hop count (15)
Cleaning up multithreading
Dying on ctrl + c

Testing-
routing convergence
md5 checks
KILL 5 to check neighbour updates.
Cpu usage monitoring

Do we need more outport ports to avoid congestion? Offset periodic prevents this occurrance?
Doc strings 

ERRORS TO FIX
**config1 only**traceback error at runtime- line 94 in update_table, line 65 in decode_table (struct error: bad char in struct format).

**UPDATE LOG**
Made a executable run shell script NOTE: need to give terminal permission to run with:
    chmod +x run.sh    ----this only needs to be done once
13/04---- implemented random timer for 3 seconds updates (+/- 20%)

16/04
added working timeout and garbage timers. NOTE- is efficient but could probably cut a few operations somewhere if needed
Routing-tables are updated network wide when 1 router drops HOWEVER new routes are sometimes not optimal. **Previous routes that had included a hop through the now deleted router are not being updated. FIX**- outlined in the spec page ~27ish

need to implement the reconnection of a router during the garbage timer. check if garbage timer is running for each packet recieved?? seems inefficient






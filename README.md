# Shelby_County_3d
## Motivation
Modeling an interdependent infrastructure systems consisting of water, power and gas networks located in Shelby County, initialize the network flow inter and intro networks based on population distribution
## Input data
(1) The node and edge information of a real water-power-gas networks in Shelby County (Not include any information about interdependency)
<br>(2) The population distribution of the Shelby County area
## Output
(1) The three networks with interdependency information and flow <br>
(2) Perform seismic simulation and obtain the result of vulnerability analysis
## Contents (In running order)
* Network_Import.py: Set up the basemap of the area where the system is modeled, import the real data of the three networks, specify network objects and system objects
* Interdependency.py: Set up the object of interdependency and initialize four types of interdependency
* Network_Flow.py: Set up the flow object where the linear optimization problem is specified and solved here
* Cascad_Failure.py: Set up the simulation of initial failure and cascading failure scenarios
* plot3d.py: Visualize the interdependent infrastructure system in 3d view, as well as the link flow
<br> The other scripts are for purposes such as MC simulation several times to get performance statistically or some data postprocessing, which are omitted here.
## To run
* Firstly in Network_Import.py script, the "epsg" file requires to be located and set os.envison['PROJ_LIB'] as the value of the path
* Then run Network_Import.py - Interdependency.py - Network_Flow.py - Cascad_Failure.py - plot3d.py

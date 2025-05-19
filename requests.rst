##################
Requests
##################


* Input synapse percent based normalization function 
  #. Score connectivity weighting by percent of total input synapse count the target neuron/population accounts for
  #. For postsynaptic target scales larger than a single neuron, average over all individual target neurons 
  #. For presyanaptic target scales larger than a single neuron, sum the input synapse counts from all neurons of the specified population to calculate the percent (and average over the target neuron population if more than one)

* (Tianhao): A function that automatically only analyzes one side of the hemisphere if the other side is clipped in the hemibrain connectome. This might not be a big problem for the EB/PB connectivity, but will hugely affect LAL/Gall. Basically if we want to analyze those regions, I would like only neuron connectivity not clipped being selected for analysis.

* (Tianhao): A function that potentially lets me adjust the threshold of qualified synapses (if possible) I am not sure whether we could directly view and change these parameters (it's doable on flywire but maybe not here in hemibrain).

* (Aryanna): Search for tri-synapses: find synapses from a specified neuron population onto synapses between two other types of neurons.
  #. Identify all target synapse connections on target neuron and locations
  #. Calculate all regions of interest (specified radius around target synapse connections)
  #. Identify all synases of the specified neuron population onto the target neuron
  #. Filter identified synapses by location (select only ones that fall within the region of interest)
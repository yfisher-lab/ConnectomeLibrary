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

* (Lily): A function that visualizes the outputs of neuromodulatory neurons and determines the distance from synapse(s) between other sets of neurons
  #. Inputs: neuromodulatory neuron(s? Multiple of one type if possible), neuron A, neuron B
  #. Outputs: plot of neuromodulatory output sites and synapse location of neuron A and B, distance between neuromodulatory output sites and neuron A/B synapse
    #. Ideally this could work with multiple cells i.e. classes of neurons, but a function that finds the avg distance or nearest neuromodulatory release site from a synapse could be useful to just iterate across cell types

* (Sansa) Input: a subtype of ∆7 (eg. L7R2, L4R5 etc.), Outputs:
  #. Function 1: for each ∆7 of this subtype, output a table summarizing the synapse count between this ∆7 and each type of its upstream neurons
  #. function 2: for each ∆7 of this subtype, output a table summarizing the synapse count between this ∆7 and each its upstream ∆7
  #. function 3: for each ∆7-∆7(of the input subtype) connection, output a table containing the each synapse location (xyz) and categorize each synapse according to ∆7 cell structure (axon terminals vs dendrite) (i am not sure if this is possible but i am thinking about categorizing based on the distance between each 2 synapses?)
  #. function 4: for each ∆7-∆7(of the input subtype) connection, a visualization of all synapse location (each pair in different colors) (i have made something like this (see pic below), but i am not sure if this is the best way to visualize)
  #. Function 5: for each ∆7 of this subtype, output a table (or a visualization, unsure which is better) showing the all glutamatergic input to it. (This one is kinda related to Aryanna’s request.)


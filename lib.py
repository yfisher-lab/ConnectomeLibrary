import numpy as np
import pandas as pd

import bokeh
import hvplot.pandas
import holoviews as hv

import bokeh.palettes
from bokeh.plotting import figure, show, output_notebook

import neuprint



TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJlbWFpbCI6Imt5bGllaHVjaEBiZXJrZWxleS5lZHUiLCJsZXZlbCI6Im5vYXV0aCIsImltYWdlLXVybCI6Imh0dHBzOi8vbGgzLmdvb2dsZXVzZXJjb250ZW50LmNvbS9hL0FDZzhvY0tpVkJGeHFzT1JxRlhnNnNOX0xIWnd4RjRoWDJORWh4WFBpY2hDaEV1Qjdsei0yUT1zOTYtYz9zej01MD9zej01MCIsImV4cCI6MTkyMjI1NDAyMH0.WLushXPCMuxMHltv_LUpoVmhtGyZSTZw08ShIrEboLY"

c = neuprint.Client('neuprint.janelia.org', 'hemibrain:v1.2.1', TOKEN)


# for given connectivity matrix, threshold connections to a given connection strength
# --> by total number of synapses onto neurons of a given type
# --> by the overall number of synapses onto the given post-synaptic neuron
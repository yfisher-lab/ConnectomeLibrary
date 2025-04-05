import numpy as np
import pandas as pd

import bokeh
import hvplot.pandas
import holoviews as hv

import bokeh.palettes
from bokeh.plotting import figure, show, output_notebook

import neuprint




def skeleton_synapse_visualization(body_Id, type_pre=None, type_post=None, rois_pre=None, rois_post=None, top=None, primary_only=True, skeleton_color=bokeh.palettes.Inferno3[0], pre_palett=None, post_palett=None, loop_colors=True, dim=2, synapse_size=None, batch_size=None):
    """ Function returning a graphic of the skeleton of neuron specified by body_Id with the desired synapses plotted colored by pre/post synpase and neuron subtype
        * body_Id (int): body ID of the given neuron would you like to examine
        * type_pre (str): type of neuron to examine synapses onto the given neuron from
            - Leave as None if only interested in post synaptic connections
        * type_post (str): type of neuron to examine synapses from the given neuron onto
            - Leave as None if only interested in pre synaptic connections
        * rois_pre (list of str): return only pre-synaptic connections within the given ROIs, leave as None if interested in all synapses
        * rois_post (list of str): return only post-synaptic connections within the given ROIs, leave as None if interested in all synapses
        * top (int): number of neurons to visualize connections from/to
            - If left as None will return synapses from/to all neurons matching the query, otherwise returns synapses from/to specified number of neurons sorted by highest number of synapses
        * primary_only (bool): return only primary synapses of the given type
        * skeleton_color (bokeh palett string): desired color descriptor for skeleton (default: black)
        * pre_palett (bokeh palett object): palett to use for pre-synaptic connections
        * post_palett (bokeh palett object): palett to use for post-synaptic connections
        * loop_colors (bool): flag for weather or not to repeat colors over multiple neurons 
            - TIP: if you are plotting connections from less than ~100 neurons you should leave this as 'True' or the difference bewteen synapses of different neurons will be very hard to visually distingish 
            - NOTE: The maximum number of colors avaiable in the palettes is 256 so if you are plotting connections to more neurons than the colors will be repeated regardless of how you set this flag
        * dim ([2,3]): dimensionality of the rendering (pick 2 or 3)
        * synapse_size (int): controls size of plotted synapses on the skeleton
        * batch_size (int): batch size for fetch_synapse_connections call
            - Decrease this number if you experience timeouts while running this function
    """
    # TODO: add synapse_size variable
    # TODO: add dim variable 
    # TODO: add batch_size support
    assert type_pre or type_post, "Error: must specify either pre or post synaptic neuron type"
    neuron_cri = neuprint.NeuronCriteria(bodyId=body_Id)
    p = figure()
    p.y_range.flipped = True
    s = neuprint.skeleton.fetch_skeleton(body_Id, format='pandas')
    s['bodyId'] = body_Id
    s['color'] = skeleton_color
    s = s.merge(s, 'inner', left_on=['bodyId', 'link'], right_on=['bodyId', 'rowId'], suffixes=['_child', '_parent'])
    p.segment(x0='x_child', x1='x_parent', y0='z_child', y1='z_parent', color='color_child', source=s)
    
    pre_top_conns = None
    post_top_conns = None
    if type_pre:
        upstream_cri = neuprint.NeuronCriteria(type=type_pre+'.*') if type_pre else None
        pre_syn_cri = neuprint.SynapseCriteria(rois=rois_pre, primary_only=primary_only)
        print("Fetching pre-synaptic connections...")
        pre_conn_df = neuprint.fetch_synapse_connections(upstream_cri, neuron_cri, pre_syn_cri)
        pre_neurons, _ = neuprint.fetch_neurons(pre_conn_df['bodyId_pre'].unique())
        pre_conn_df = neuprint.utils.merge_neuron_properties(pre_neurons, pre_conn_df, 'instance')
        if top: 
            pre_top_conns = pre_conn_df['instance_pre'].value_counts().head(top)
        else:
            pre_top_conns = pre_conn_df['instance_pre'].value_counts()
        if not pre_palett:
            lc = len(pre_top_conns)
            if lc <= 11:
                pre_palett = bokeh.palettes.Plasma[lc if lc>2 else 3]
            elif lc > 100:
                pre_palett = bokeh.palettes.Plasma256
            else:
                if loop_colors:
                    pre_palett = bokeh.palettes.Plasma11
                else:
                    pre_palett = bokeh.palettes.Iridescent23
        pre_points = pre_conn_df.query('instance_pre in @pre_top_conns.index').copy()
        pre_colors = (pre_palett * (len(pre_points) // len(pre_palett) + 1))[:len(pre_points)]
        pre_points['color'] = pre_points['instance_pre'].map(dict(zip(pre_top_conns.index, pre_colors)))
        p.scatter(pre_points['x_pre'], pre_points['z_pre'], color=pre_points['color'])
    if type_post:
        downstream_cri = neuprint.NeuronCriteria(type=type_post+'.*') if type_post else None
        post_syn_cri = neuprint.SynapseCriteria(rois=rois_post, primary_only=primary_only)
        print("Fetching post-synaptic connections...")
        post_conn_df = neuprint.fetch_synapse_connections(neuron_cri, downstream_cri, post_syn_cri)
        post_neurons, _ = neuprint.fetch_neurons(post_conn_df['bodyId_post'].unique())
        post_conn_df = neuprint.utils.merge_neuron_properties(post_neurons, post_conn_df, 'instance')
        if top:
            post_top_conns = post_conn_df['instance_post'].value_counts().head(top)
        else:
            post_top_conns = post_conn_df['instance_post'].value_counts()
        if not post_palett:
            lc = len(post_top_conns)
            if lc <= 11:
                post_palett = bokeh.palettes.Viridis[lc if lc>2 else 3]
            elif lc > 100:
                post_palett = bokeh.palettes.Viridis256
            else:
                if loop_colors:
                    post_palett = bokeh.palettes.Viridis11
                else:
                    post_palett = bokeh.palettes.Viridis256
        post_points = post_conn_df.query('instance_post in @post_top_conns.index').copy()
        post_colors = (post_palett * (len(post_points) // len(post_palett) + 1))[:len(post_points)]
        post_points['color'] = post_points['instance_post'].map(dict(zip(post_top_conns.index, post_colors)))
        p.scatter(post_points['x_post'], post_points['z_post'], color=post_points['color'])
    show(p)

    return pre_top_conns, post_top_conns



# for given connectivity matrix, threshold connections to a given connection strength
# --> by total number of synapses onto neurons of a given type
# --> by the overall number of synapses onto the given post-synaptic neuron

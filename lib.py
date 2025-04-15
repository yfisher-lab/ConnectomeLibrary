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


def fetch_connectivity(target_scale, conn_scale, conn_type, target_id, conn_id=None, rois=None):
    """ Fetch a connectivity matrix between specified neurons/subtypes/types avoiding over/under counting of synapses 
        * target_scale (str): indicates scale to analyze neuron(s) of interest on
            - 'neuron': normalize conections to/from a specific neuron 
                - NOTE: must specify neuprint neuron integer bodyId as 'target_id' argument
            - 'instance': normalize connections over an entire instance (subtype) of neurons (ie 'PEN_b(PB06b)_L4')
                - NOTE: must specify neuprint neuron instance (subtype) name as 'target_id' argument 
            - 'type': normalize connections over an entire type of neurons (ie 'PEN_b(PEN2)')
                - NOTE: must specify neuprint neuron type name as 'target_id' argument 
        * conn_scale (str): indicates scale over which to analyze connections to/from target neuron(s)
            - 'neuron': normalize connections to/from a sprcific neuron
                - NOTE: must specify neuprint neuron integer bodyId as 'conn_id' argument
            - 'instance': nomalize connections to/from an entire instance (subtype) of neurons (ie 'PEN_b(PB06b)_L4')
                - NOTE: must specify neuprint neuron instance (subtype) name as 'conn_id' argument
            - 'type': normalize connections to/from an entire type of neurons (ie 'PEN_b(PEN2)')
                - NOTE: must specify neuprint neuron type name as 'conn_id' argument
            - 'all': normalize connections to/from all pre/post synaptic neurons
        * conn_type (str): indicates weather to analyzing inputs or outputs to/from a given neuron/instance/type
            - 'pre': normalize presynaptic connections (analyze relative contributions of inputs) 
            - 'post': normalize postsynaptic connections (analyze relative output strengths)
        * target_id (int or str): neuprint identifier for target neuron(s) ID/instance/type
            - NOTE: nust exactly match neuron's identifier in the neuprint database including capatilization
        * conn_id (int, str, or None): neuprint identifier for connecting neuron(s) ID/instance/type
            - Leave as 'None' if you're interested in all connections to/from the target neuron(s)
            - NOTE: nust exactly match neuron's identifier in the neuprint database including capatilization
        * rois (list of str): list of string identifiers for all ROIs from which to analyze connections from
            - Leave as None if interested in all connections bettween the specified neurons, regardless of location 
    """
    assert target_scale in ['neuron', 'instance', 'type'], "Error: must specify target scale of 'neuron', 'instance', or 'type'"
    assert conn_scale in ['neuron', 'instance', 'type', 'all'], "Error: must specify connection scale of 'neuron', 'instance', 'type', or 'all'"
    assert conn_type in ['pre', 'post'], "Error: must specify connection type of 'pre' or 'post'"
    if target_scale == 'neuron':
        assert type(target_id) == int, "Error: must specify integer bodyId for target neuron"
        target_nc = neuprint.NeuronCriteria(bodyId=target_id)
    elif target_scale == 'instance':
        assert type(target_id) == str, "Error: must specify string neuprint instance name for target neuron subtype"
        target_nc = neuprint.NeuronCriteria(instance=target_id)
    else:
        assert type(target_id) == str, "Error: must specify string neuprint type name for connecting neuron type"
        target_nc = neuprint.NeuronCriteria(type=target_id)
    if conn_scale == 'neuron':
        assert type(conn_id) == int, "Error: must specify integer bodyId for connecting neuron"
        conn_nc = neuprint.NeuronCriteria(bodyId=conn_id)
    elif conn_scale == 'instance':
        assert type(conn_id) == str, "Error: must specify string neuprint instance name for connecting neuron subtype"
        conn_nc = neuprint.NeuronCriteria(instance=conn_id)
    elif conn_scale == 'type':
        assert type(conn_id) == str, "Error: must specify string neuprint type name for connecting neuron type"
        conn_nc = neuprint.NeuronCriteria(type=conn_id)
    else:
        conn_nc=None
    if conn_type == 'pre':
        pre_nc = conn_nc
        post_nc = target_nc
    else:
        pre_nc = target_nc
        post_nc = conn_nc
    neurons, conns = neuprint.fetch_adjacencies(pre_nc, post_nc, rois=rois, min_roi_weight=1, include_nonprimary=False)
    conns = neuprint.merge_neuron_properties(neurons, conns, ['type', 'instance'])
    conns.sort_values('weight', ascending=False, inplace=True)
    # manually remove any 'NotPrimary' synapses (even with include_nonprimary=False some are included!)
    conns = conns[conns['roi']!='NotPrimary']
    return conns


def normalize_connectivity(target_scale, conn_scale, conn_type, target_id, conn_id=None, rois=None, norm_mode='syn_cnt'):
    """ Normalize a connectivity matrix between specified neurons/subtypes/types 
        * target_scale (str): indicates scale to analyze neuron(s) of interest on
            - 'neuron': normalize conections to/from a specific neuron 
                - NOTE: must specify neuprint neuron integer bodyId as 'target_id' argument
            - 'instance': normalize connections over an entire instance (subtype) of neurons (ie 'PEN_b(PB06b)_L4')
                - NOTE: must specify neuprint neuron instance (subtype) name as 'target_id' argument 
            - 'type': normalize connections over an entire type of neurons (ie 'PEN_b(PEN2)')
                - NOTE: must specify neuprint neuron type name as 'target_id' argument 
        * conn_scale (str): indicates scale over which to analyze connections to/from target neuron(s)
            - 'instance': nomalize connections to/from an entire instance (subtype) of neurons (ie 'PEN_b(PB06b)_L4')
                - NOTE: must specify neuprint neuron instance (subtype) name as 'conn_id' argument
            - 'type': normalize connections to/from an entire type of neurons (ie 'PEN_b(PEN2)')
                - NOTE: must specify neuprint neuron type name as 'conn_id' argument
            - 'all': normalize connections to/from all pre/post synaptic neurons
        * conn_type (str): indicates weather to analyzing inputs or outputs to/from a given neuron/instance/type
            - 'pre': normalize presynaptic connections (analyze relative contributions of inputs) 
            - 'post': normalize postsynaptic connections (analyze relative output strengths)
        * target_id (int or str): neuprint identifier for target neuron(s) ID/instance/type
            - NOTE: nust exactly match neuron's identifier in the neuprint database including capatilization
        * conn_id (int, str, or None): neuprint identifier for connecting neuron(s) ID/instance/type
            - Leave as 'None' if you're interested in all connections to/from the target neuron(s)
            - NOTE: nust exactly match neuron's identifier in the neuprint database including capatilization
        * rois (list of str): list of string identifiers for all ROIs from which to analyze connections from
            - Leave as None if interested in all connections bettween the specified neurons, regardless of location 
        * norm_mode (str): indicates the method of normalization to be preformed
            - 'syn_cnt': normalize connection strength between target neuron/instance/type and connection neuron/instance/type by average number of connections between target neuron/instance/type and connection neuron/instance/type (ignoring cell counts)
            - 'syn_tot' : normalize connection strength between target neuron/instance/type and connection neuron/instance/type by average total number of synapses to/from target neuron/instance/type (ignoring cell counts) 
            - 'cell_cnt': normalize connection strength between target neuron/instance/type and connection neuron/instance/type by average number of target neuron/instance/type neurons connecting to (pre/post) connection neuron/instance/type neurons (ignoring synapse counts)
            - 'cell_tot': normalize connection strength between target neuron/instance/type and connection neuron/instance/type by total number of neurons connecting to target neuron/instance/type neurons (ignoring synapse counts)
    """
    assert norm_mode in ['syn_cnt', 'syn_tot', 'cell_cnt', 'cell_tot'], "Error: must specify norm mode of 'syn_cnt', 'syn_tot', 'cell_cnt', or 'cell_tot'"
    if conn_scale == 'neuron':
        print("Cannot normalize connections on the scale of individual neurons. Nothing to do.")
        return None
    target_type = ('pre' if conn_type=='post' else 'post')
    ts_id = target_scale + '_' + target_type
    cs_id = conn_scale + '_' + conn_type
    conns = fetch_connectivity(target_scale, conn_scale, conn_type, target_id, conn_id, rois)
    if norm_mode == 'syn_cnt':
        avg_syn_cnt = sum(conns['weight']) / len(conns['weight'])
        conns['norm_syn_cnt'] = conns['weight'] / avg_syn_cnt
        conns['syn_cnt'] = conns['weight']
        conns = conns[['bodyId_pre', 'instance_pre', 'type_pre', 'bodyId_post', 'instance_post', 'type_post', 'roi', 'syn_cnt', 'norm_syn_cnt']]
    elif norm_mode == 'cell_cnt':
        cell_cnts = {}
        target_ids = conns['bodyId_'+target_type].unique()
        for bid in target_ids:
            cell_cnts[bid] = len(conns[conns['bodyId_'+target_type]==bid])
        avg_cnt = sum(cell_cnts.values()) / len(cell_cnts)
        cell_data = {'bodyId_'+target_type: cell_cnts.keys(), ts_id: [target_id]*len(cell_cnts), cs_id: [conn_id]*len(cell_cnts), conn_scale+'_cell_cnt_'+conn_type: cell_cnts.values(), 'norm_'+conn_scale+'_cell_cnt_'+conn_type: [x/avg_cnt for x in cell_cnts.values()] }
        conns = pd.DataFrame(cell_data)
        conns.sort_values(conn_scale+'_cell_cnt_'+conn_type, ascending=False, inplace=True)
    else:
        tot_conns = fetch_connectivity(target_scale=target_scale, conn_scale='all', conn_type=conn_type, target_id=target_id, conn_id=None, rois=None)
        if norm_mode == 'syn_tot':
            # calculate average pre/post synapse number over all neurons of target instance/type 
            avg_tot_syn_cnt = sum(tot_conns['weight']) / len(tot_conns['weight'])
            # normalize synapse count in conn table 
            conns['global_norm_syn_cnt'] = conns['weight'] / avg_tot_syn_cnt
            conns['syn_cnt'] = conns['weight']
            conns = conns[['bodyId_pre', 'instance_pre', 'type_pre', 'bodyId_post', 'instance_post', 'type_post', 'roi', 'syn_cnt', 'global_norm_syn_cnt']]
        else:
            # calaculate avarage pre/post synaptic cell count over all target instance/type
            # calc norm connection strength 
            target_ids = tot_conns['bodyId_'+target_type].unique()
            glob_cell_cnts = {}
            cell_cnts = {}
            for bid in target_ids:
                glob_cell_cnts[bid] = len(tot_conns[tot_conns['bodyId_'+target_type]==bid])
                cell_cnts[bid] = len(conns[conns['bodyId_'+target_type]==bid])
            glob_avg_cell_cnt = sum(glob_cell_cnts.values()) / len(glob_cell_cnts.values())
            cell_data = { 'bodyId_'+target_type: glob_cell_cnts.keys(), ts_id: [target_id]*len(glob_cell_cnts), 'tot_cell_cnt_'+conn_type: glob_cell_cnts.values(), cs_id: [conn_id]*len(glob_cell_cnts), conn_scale+'_cell_cnt_'+conn_type: cell_cnts.values(), 'norm_'+conn_scale+'_cell_cnt_'+conn_type: [x/glob_avg_cell_cnt for x in cell_cnts.values()] }
            conns = pd.DataFrame(cell_data)
            conns.sort_values(conn_scale+'_cell_cnt_'+conn_type, ascending=False, inplace=True)
    return conns


def visualize_conn(conn_df, pre_scale, post_scale, sort_by='type', weight_col='weight', height=500, width=700, x_ax_rot=60):
    """ Function to plot connectivity dataframe as a heatmap
        * conn_df (pandas DataFrame object): connectivity table to plot
        * pre_scale (str): scale at which to group presynaptic neurons (plotted along the y-axis)
            - 'neuron': plot individual neurons labled by integer neuprint bodyId
            - 'instance': plot neurons grouped by instance labled by neuprint instance string
            - 'type': plot neurons grouped by type labled by neuprint type string
        * post_scale (str): scale at which to group postsynaptic neurons (plotted along the x-axis)
            - 'neuron': plot individual neurons labled by integer neuprint bodyId
            - 'instance': plot neurons grouped by instance labled by neuprint instance string
            - 'type': plot neurons grouped by type labled by neuprint type string
        * sort_by (str): desired ordering of neurons, options: ['instance', 'type'] 
        * weight_col (str): label of the column containing the weights to be plotted
        * height (int): desired hight of the plot
        * width (int): desired width of the plot
        * x_ax_rot (int): desired degree rotation of the x-axis lables
    """
    # TODO: figure out how to plot neuron groupings at different scales allong x and y axies
    conn_mx = neuprint.connection_table_to_matrix(conn_df, group_cols=(pre_scale, post_scale), weight_col=weight_col, sort_by=sort_by)
    conn_mx.index = conn_mx.index.astype(str)
    conn_mx.columns = conn_mx.columns.astype(str)
    return conn_mx.hvplot.heatmap(height=height, width=width, xaxis='top').opts(xrotation=x_ax_rot)


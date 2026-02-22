# -*- coding: utf-8 -*-
"""
Created on Fri Feb 21 07:51:18 2025

@author: Daniel
"""

import networkx as nx;

def network_MFNIP (G):
    
    Gm = G.copy();
    
    for i,j in G.edges:
        if G.edges[i,j]['special'] == 1:
            Gm.edges[i,j]['capacity'] = 1;
        else:
            Gm.edges[i,j]['capacity'] = 10000;
            
    return Gm;
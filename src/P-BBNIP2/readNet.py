# -*- coding: utf-8 -*-
"""
Created on Wed Jan 29 14:30:22 2025

@author: Daniel
"""
import networkx as nx;
import pandas as pd;
import csv;


def readNet(network):
    
    nVictims = 0;
    nTraffickers = 0;
    nBottoms = 0;
    
    G = nx.DiGraph();
    with open(network, newline='') as f:
        reader = csv.reader(f);
        row1 = next(reader);
        s = int(row1[0]);
        t = int(row1[1]);
            
        data = pd.read_csv(network, skiprows=1, header=None);
        n_edge = len(data.index + 1);
            
        for i in range(n_edge):
            G.add_edge(data.iat[i,0], data.iat[i,1],
                       capacity = data.iat[i,2],
                       cost = data.iat[i,3],
                       special = data.iat[i,4],
                       trafficker = data.iat[i,5],
                       bottom = data.iat[i,6],
                       victim = data.iat[i,7]);
        
    for i,j in G.edges:
        if G.edges[i,j]['victim'] == 1:
            nVictims += 1;
        elif G.edges[i,j]['trafficker'] == 1:
            nTraffickers += 1;
        elif G.edges[i,j]['bottom'] == 1:
            nBottoms += 1;
                
    
    return G, s, t, nVictims, nTraffickers, nBottoms;
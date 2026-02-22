# -*- coding: utf-8 -*-
"""
Created on Thu Jan 30 10:32:25 2025

@author: daniel
"""

# -*- coding: utf-8 -*-
"""
Created on Thu Jan 30 10:10:28 2025

@author: daniel
"""
import networkx as nx;
import gurobipy as gp;
from gurobipy import GRB;
from datetime import datetime;
import math;
import numpy;
from numpy import* 

def InnerProblem_Optimistic (Gamma, G, s, t):
    
    model = gp.Model("InnerOptimistic");
    
    x = model.addVars(G.edges, vtype=GRB.CONTINUOUS, lb = 0, ub = GRB.INFINITY);
    z = model.addVars(G.edges, vtype=GRB.BINARY);
    alpha = model.addVars(G.nodes, vtype=GRB.CONTINUOUS, lb = 0, ub = 1);
    theta = model.addVars(G.edges, vtype=GRB.CONTINUOUS, lb = 0, ub = 1);
           
    model.addConstrs(gp.quicksum(x[j,i] for i in G.successors(j))
                         - gp.quicksum(x[i,j] for i in G.predecessors(j)) == 0 for j in G.nodes);
            
    for i,j in G.edges:
        model.addConstr(x[i,j] <= (1-Gamma[i,j])*G.edges[i,j]['capacity']);
            
    for i,j in G.edges:
        model.addConstr(alpha[i] - alpha[j] + theta[i,j] >= 0);
            
    model.addConstr(alpha[t] - alpha[s] >= 1);
            
    model.addConstr(x[t,s] >= gp.quicksum((1-Gamma[i,j])*G.edges[i,j]['capacity']*theta[i,j]
                                                     for i,j in G.edges));
            
    for i,j in G.edges:
        if (G.edges[i,j]['special'] == 1):
            model.addConstr(x[i,j] <= G.edges[i,j]['capacity']*z[i,j]);
        else:
            model.addConstr(z[i,j] == 0);
            
    model.setObjective(gp.quicksum(z[i,j]*G.edges[i,j]['special'] for i,j in G.edges), GRB.MINIMIZE); 
            
    model.setParam("IntegralityFocus",1);
    #model.setParam("NumericFocus",2);       
    #model.setParam('TimeLimit', T_Lim);
            
    model.update();
    model.setParam("OutputFlag", 0);
    model.optimize();
    
    if model.SolCount == 0:
        print("No feasible solution available (Inner_Problem)");
        model.computeIIS();
        model.write('IISmodel.ilp');
    
    
    # X = {};
    # Z = {};
    
    # for i,j in G.edges:
    #     X[i,j] = x[i,j].x;
    #     Z[i,j] = z[i,j].x;
    
    return model.objVal;
      
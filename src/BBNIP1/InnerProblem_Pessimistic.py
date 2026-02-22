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

def InnerProblem_Pessimistic (Gamma, G, s, t, A):
    
    max_model = gp.Model("InnerPessimistic");
    
    
    x = max_model.addVars(G.edges, vtype=GRB.CONTINUOUS, lb = 0, ub = GRB.INFINITY);
    z = max_model.addVars(G.edges, vtype=GRB.CONTINUOUS, lb = 0, ub = 1);
    alpha = max_model.addVars(G.nodes, vtype=GRB.CONTINUOUS, lb = 0, ub = 1);
    theta = max_model.addVars(G.edges, vtype=GRB.CONTINUOUS, lb = 0, ub = 1);
           
    max_model.addConstrs(gp.quicksum(x[j,i] for i in G.successors(j))
                         - gp.quicksum(x[i,j] for i in G.predecessors(j)) == 0 for j in G.nodes);
            
    for i,j in G.edges:
        max_model.addConstr(x[i,j] <= (1-Gamma[i,j])*G.edges[i,j]['capacity']);
            
    for i,j in G.edges:
        max_model.addConstr(alpha[i] - alpha[j] + theta[i,j] >= 0);
            
    max_model.addConstr(alpha[t] - alpha[s] >= 1);
            
    max_model.addConstr(x[t,s] >= gp.quicksum((1-Gamma[i,j])*G.edges[i,j]['capacity']*theta[i,j]
                                                     for i,j in G.edges));
            
    for i,j in G.edges:
        if (G.edges[i,j]['special'] == 1):
            max_model.addConstr(x[i,j] >= (1/A)*z[i,j]);
        else:
            max_model.addConstr(z[i,j] == 0);
            
    max_model.setObjective(gp.quicksum(z[i,j]*G.edges[i,j]['special'] for i,j in G.edges), GRB.MAXIMIZE); 
            
    max_model.setParam("IntegralityFocus",1);
    #max_model.setParam("NumericFocus",2);       
    #max_model.setParam('TimeLimit', T_Lim);
            
    max_model.update();
    max_model.setParam("OutputFlag", 0);
    max_model.optimize();
    
    if max_model.SolCount == 0:
        print("No feasible solution available (Max-Problem)");
    
    
    X = {};
    Z = {};
    
    for i,j in G.edges:
        X[i,j] = x[i,j].x;
        Z[i,j] = z[i,j].x;
    
    return max_model.objVal;
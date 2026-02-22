import networkx as nx;
import gurobipy as gp;
from gurobipy import GRB;
import sys;
import time;
from datetime import datetime;
import csv;
import math;
import numpy;
from numpy import *;

import os;

from readNet import*;

from SO_Opt_SpecialArcs import*;

from SO_Pes_SpecialArcs import*;

from InnerProblem_Pessimistic import*;

from InnerProblem_Optimistic import*;

from pessimistic2 import*;

from optimistic2 import*;




#  main  

nNets = 5;

Budget = [32, 40, 48, 56, 64];
Rate = [0.1, 0.4, 0.7, 1];


# Define restrictions on interdiction:
# restriction = 0 (No interdiction)
# restriction = 1 (Can only remove Victims)
# restriction = 2 (Can only remove Traffickers)

restriction = 0;


    
for n in range(1, nNets+1):
    
    # ------- Set the Network Instances -----------------------
    
    # # ------ Different Capacities
    # network = "Networks/DifferentCapacities/Net10_"+str(n)+"_DifCap.csv";
    # Name = "Results/Results_"+str(n)+"/DifferentCapacities/ResultsBBNIP1_"+str(n)+"_.csv"
    # print('\n\nDifferent Capacities\n')
    
    # # ------ Same Capacities
    # network = "Networks/SameCapacities/Net10_"+str(n)+"_SameCap.csv";
    # Name = "Results/Results_"+str(n)+"/SameCapacities/ResultsBBNIP1_"+str(n)+"_.csv"
    # print('\n\nSame Capacities\n')
    
    # ------ Operations Same Capacities
    network = "Networks/OperationsSameCapacities/Net10_"+str(n)+"_OpSameCap.csv";
    Name = "Results/Results_"+str(n)+"/OperationsSameCapacities/ResultsBBNIP1_"+str(n)+"_.csv"
    print('\n\nOperations Same Capacities\n')
    
    # ----------------------------------------------------------------------------------------
    
    
    file = open(Name, "w");
    file.write('Instance,Budget,Rate,PF_points, Time\n');
    file.close();  
    
    
    
    G, s, t, nVictims, nTraffickers, nBottoms = readNet(network);

    for budget in Budget:
        
        
        for rate in Rate:
            
            now = datetime.now();
            
            start = time.time();
            
            G_r = G.copy();
            
            for i in G.successors(s):
                    G_r.edges[s,i]['capacity'] = math.floor(rate*G.edges[s,i]['capacity']);
            
            
            obj_Opt, Gamma_Opt = SO_Opt_SpecialArcs (G_r, s, t, budget, rate, restriction);
            
            obj_Pes2, Gamma_Pes2 = pessimistic2 (G_r, s, t, budget, rate, obj_Opt, restriction);
            
            obj_Pes, Gamma_Pes = SO_Pes_SpecialArcs (G_r, s, t, budget, rate, restriction); 
                                      
            obj_Opt2, Gamma_Opt2 = optimistic2 (G_r, s, t, budget, rate, obj_Pes, restriction);
            
            
            # What happens if our assumption is wrong!
            obj_Opt_Pes = InnerProblem_Pessimistic (Gamma_Opt, G_r, s, t, nVictims);
            
            obj_Pes_Opt = InnerProblem_Optimistic (Gamma_Pes, G_r, s, t);
            
            
            
            print('\nNet = %g, Budget = %g, Rate = %g\n' %(n, budget, rate));
            # Restriction on Interdiction
            if restriction == 0:
                print('\nNo Restriction on Interdiction!\n')
        
            elif restriction == 1:
                print('\nCan only remove Victims!\n')
            
            elif restriction == 2:
                print('\nCan only remove Traffickers!\n')
            
            
            delta = obj_Opt2 - obj_Opt;
            
            if delta == 0:
                PF_points = 1;
                print('Only 1 PF Point:');
                print('PF Point (Opt, Pes) = (%d, %d)\n' %(obj_Opt, obj_Pes2));
            
            elif delta == 1:
                PF_points = 2;
                print('Only 2 PF Points:');
                print('PF Point1 (Opt, Pes) = (%d, %d)' %(obj_Opt, obj_Pes2));
                print('PF Point2 (Opt, Pes) = (%d, %d)\n' %(obj_Opt2, obj_Pes));
            
            else:
                PF_points = 2;
                print('Multiple PF Points\n');
                print('PF Point (Opt, Pes) = (%d, %d)' %(obj_Opt, obj_Pes2));
                
                TEMP_OPT = [];
                TEMP_PES = [];
                
                TEMP_GAMMA = {};
                
                temp_opt = obj_Opt + 1;
                
                ctr = 0;
                
                while temp_opt < obj_Opt2:
                    
                    temp_pes, Gamma_temp_pes = pessimistic2 (G_r, s, t, budget, rate, temp_opt, restriction);
                    
                    if temp_pes <= obj_Pes2 - 1 and temp_pes not in TEMP_PES: 
                        print('\nIntermediate Point (Opt, Pes) = (%g, %g)\n' %(temp_opt, temp_pes));
                        
                        TEMP_OPT.append(temp_opt);
                        TEMP_PES.append(temp_pes);
                        TEMP_GAMMA[ctr] = Gamma_temp_pes;
                        
                        ctr += 1;
                        PF_points += 1;
                    else:
                        print("\nDominated point!\n")
                    
                    temp_opt += 1;
                    
                print('PF Point (Opt, Pes) = (%d, %d)\n' %(obj_Opt2, obj_Pes));
            
            del G_r;
            
            end = time.time();
            
            runTime = round(end - start, 2);
            
            
            ##################################################################
            
            # # ------ Different Capacities
            # Name1 = "Results/Results_"+str(n)+"/DifferentCapacities/ResultsBBNIP1_Network_"+str(n)+"_"+str(budget)+"_"+str(rate)+".txt";
            
            # # ------- Same Capacities
            Name1 = "Results/Results_"+str(n)+"/SameCapacities/ResultsBBNIP1_Network_"+str(n)+"_"+str(budget)+"_"+str(rate)+".txt";
            
            # --------- Operations Same Capacities
            Name1 = "Results/Results_"+str(n)+"/OperationsSameCapacities/ResultsBBNIP1_Network_"+str(n)+"_"+str(budget)+"_"+str(rate)+".txt";
            
            #######################################################################################################
            
            
            
            
            file2 = open(Name1, "w");
            file2.write('Instance %s, Budget %g, Rate %g\n' %(network, budget, rate));
            file2.write('Instance executed at: %s \n' %now.strftime("%c"));
            
            if restriction == 0:
                file2.write('\nNo restriction on interdiction!\n')
                
            elif restriction == 1:
                file2.write('\nCan only remove Victims!\n')
                
            elif restriction == 2:
                file2.write('\nCan only remove Traffickers!\n')

            
            file2.write('\nPareto Point: (%g, %g)\n' %(obj_Opt, obj_Pes2))
            file2.write('Interdiction:\n')
            for i,j in G.edges:
                if Gamma_Pes2[i,j] > 0.0001:
                    if G.edges[i,j]['trafficker'] == 1:
                        file2.write('(%g, %g), %s\n' %(i,j, 'Trafficker'));
                    elif G.edges[i,j]['bottom'] == 1:
                        file2.write('(%g, %g), %s\n' %(i,j, 'Bottom'));
                    elif G.edges[i,j]['victim'] == 1:
                        file2.write('(%g, %g), %s\n' %(i,j, 'Victim'));
                    else:
                        file2.write('(%g, %g), %s\n' %(i,j, 'Problem with classification of arcs!'));
            
            if delta == 0:
                file2.close(); 
            
            elif delta == 1:
                file2.write('\nPareto Point: (%g, %g)\n' %(obj_Opt2, obj_Pes))
                file2.write('Interdiction:\n')
                for i,j in G.edges:
                    if Gamma_Opt2[i,j] > 0.0001:
                        if G.edges[i,j]['trafficker'] == 1:
                            file2.write('(%g, %g), %s\n' %(i,j, 'Trafficker'));
                        elif G.edges[i,j]['bottom'] == 1:
                            file2.write('(%g, %g), %s\n' %(i,j, 'Bottom'));
                        elif G.edges[i,j]['victim'] == 1:
                            file2.write('(%g, %g), %s\n' %(i,j, 'Victim'));
                        else:
                            file2.write('(%g, %g), %s' %(i,j, 'Problem with classification of arcs!'));
                
                file2.close();        
                
            else:
                it = 0;
                while len(TEMP_OPT) >= 1:
                    
                    file2.write('\nPareto Point: (%g, %g)\n' %(TEMP_OPT.pop(0), TEMP_PES.pop(0)))
                    file2.write('Interdiction:\n')
                    
                    for i,j in G.edges:
                        if TEMP_GAMMA[it][i,j] > 0.0001:
                            if G.edges[i,j]['trafficker'] == 1:
                                file2.write('(%g, %g), %s\n' %(i,j, 'Trafficker'));
                            elif G.edges[i,j]['bottom'] == 1:
                                file2.write('(%g, %g), %s\n' %(i,j, 'Bottom'));
                            elif G.edges[i,j]['victim'] == 1:
                                file2.write('(%g, %g), %s\n' %(i,j, 'Victim'));
                            else:
                                file2.write('(%g, %g), %s\n' %(i,j, 'Problem with classification of arcs!'));

                    it += 1;
                
                file2.write('\nPareto Point: (%g, %g)\n' %(obj_Opt2, obj_Pes))
                file2.write('Interdiction:\n')
                for i,j in G.edges:
                    if Gamma_Opt2[i,j] > 0.0001:
                        if G.edges[i,j]['trafficker'] == 1:
                            file2.write('(%g, %g), %s\n' %(i,j, 'Trafficker'));
                        elif G.edges[i,j]['bottom'] == 1:
                            file2.write('(%g, %g), %s\n' %(i,j, 'Bottom'));
                        elif G.edges[i,j]['victim'] == 1:
                            file2.write('(%g, %g), %s\n' %(i,j, 'Victim'));
                        else:
                            file2.write('(%g, %g), %s' %(i,j, 'Problem with classification of arcs!'));
                
                file2.close();        
            
            
            write = [n, budget, rate, PF_points, runTime];
            with open(Name, 'a', newline='') as csvfile:
                csvwriter = csv.writer(csvfile);
                csvwriter.writerow(write);
                csvfile.close();
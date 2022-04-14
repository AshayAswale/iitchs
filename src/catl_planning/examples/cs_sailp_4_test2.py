# DISTRIBUTION STATEMENT A. Approved for public release. Distribution is unlimited.

# This material is based upon work supported by the Under Secretary of Defense for 
# Research and Engineering under Air Force Contract No. FA8702-15-D-0001. Any 
# opinions, findings, conclusions or recommendations expressed in this material 
# are those of the author(s) and do not necessarily reflect the views of the Under 
# Secretary of Defense for Research and Engineering.

# (C) 2021 Massachusetts Institute of Technology.

# Subject to FAR52.227-11 Patent Rights - Ownership by the contractor (May 2014)

# The software/firmware is provided to you on an As-Is basis

# Delivered to the U.S. Government with Unlimited Rights, as defined in DFARS 
# Part 252.227-7013 or 7014 (Feb 2014). Notwithstanding any copyright notice, U.S. 
# Government rights in this work are defined by DFARS 252.227-7013 or DFARS 
# 252.227-7014 as detailed above. Use of this work other than as specifically 
# authorized by the U.S. Government may violate any copyrights that exist in this 
# work.

# SPDX-License-Identifier: BSD-3-Clause

import numpy as np
from lomap.classes.ts import Ts

# For creating Output File Directories, if they don't exist.
from pathlib import Path

import sys
if sys.flags.debug:
    import pdb

##########################################################
# File Names
##########################################################
ts_filename='./catl_planning/TransitionSystems/sailp_4_test1.yaml'
save_filename = './OutputFiles/cs_sailp_4_test1/'
output_path = './OutputFiles/cs_sailp_4_test1/'

# Check if directories for save_filename and output_path exist.
# If not, create them.
Path(save_filename).mkdir(parents=True, exist_ok=True)
Path(output_path).mkdir(parents=True, exist_ok=True)

#This reloads prior constraints or solutions.
load_old_files = False
reload_file = None #Would be a string file name


##########################################################
# Final Output Options
##########################################################
sim_dynamics = False #Should we run pure pursuit?
sim_wheel_base = 0.0 #describes turning radius of agents in simulator

k = 0.5  # look forward gain
Lfc = 1.0  # look-ahead distance
Kp = 2.3  # speed proportional gain
dt = 0.8  # [s]
L = 20.0  # [m] wheel base of vehicle

old_nearest_point_index = None
show_animation = False


kml_output = False
corner_coor = (41.98,-70.65) #Plymouth Rock
# Boston Harbor: (42.36,-70.95)

txt_out = False


##########################################################
# Specification and Agents
##########################################################

grave_state = 0
replan_grave = 'q0'

#Key Objectives:

DefendA1 = 'G[0,75]F[0,35] T(3,DA,{(Def,1)})'
DefendC1 = 'G[0,90] T(1,DC,{(Def,1)})'
DefendB1= 'G[0,75]F[0,35] T(3,DB,{(Def,1)})'
DefendC2 = 'F[80,90]T(1,DC,{(Def,3)})'

ScienceA1 = 'F[0,60] T(20,SA,{(SciA,1)})'
ScienceB1 = 'F[0,60] T(20,SB,{(SciB,1)})'

VisitABC = 'F[0,20] T(1,DA,{(Def,1)}) && F[20,40] T(1,DC,{(Def,2)}) && F[40,60] T(1,DB,{(Def,1)})'

DefendSciA = '(G[0,75]F[0,35]T(3,DA,{(Def,1)})) U[0,30] T(20,SA,{(SciA,1)})'
DefendSciB = '(G[0,75]F[0,35]T(3,DB,{(Def,1)})) U[0,30] T(20,SB,{(SciB,1)})'


#formula = '(' + DefendSciA + '&&' + ScienceA1 + ')||(' + DefendSciB + '&&' + ScienceB1 + ')'
#formula = DefendSciA + '&&' + ScienceA1 + '&&' + DefendSciB + '&&' + ScienceB1 
#formula = VisitABC
formula = DefendA1 + '&&' + DefendB1 + '&&' + DefendC1 + '&&' + ScienceA1 + '&&' + ScienceB1 + '&&' + DefendC2

agents = [('q5', {'Def','SciA'}), ('q5', {'Def','SciA'}),  ('q5', {'Def','SciB'}), ('q5',{'Def','SciB'})]


##########################################################
#ROS Setup
##########################################################

ros_name_index_mapping = ['AGENT_0','AGENT_1','AGENT_2','AGENT_3','AGENT_4']
sim_2_world_converts = None#[-0.4, -0.1, -0.059, 0.058] #[x_off,y_off,scaley,scalex]


#Show Transition World
show_visuals = True

#Show generates a plot of all of the trajectories - It is not automatically saved
show_sol = True

#Record generates a video of the trajectories being executed in time - it is saved automatically
record_sol = True

robust = False # True
regularize=True
alpha = 0.5
upper_bound = True
num_agents = 4

#Different numbers mean they operate at diffent levels and wont collide
cap_height_map = [0,0,0,0]
agent_radius = .5*np.ones(num_agents,'int')
##CODE CURRENTLY CONSIDERS ALL AGENTS AT HEIGHT MAP 0 - NEEDED TO PARALLELIZE EASILY

##########################################################
# Lower Level Trajectory Planning Variables
##########################################################

local_obstacles = [[
        [0,0,0],
        [0,0,0]
    ],
    [
        [0,0,0],
        [0,0,0]
    ]]

'''
These are obstalces not in the optimization but need to be considered in trajectories.
They are circles (x,y,r) and then each outter array is for a given height.
obstaclesList  = [[
        [0,0,0],
        [0,0,0]
    ],
    [
        [0,0,0],
        [0,0,0]
    ],
    [
        [0,0,0],
        [0,0,0]
    ]
    ]
'''
#Number of restarts allowed for one trajectory before restarting from scratch
max_attempts = 1
#Time allowed for single tree to be built before restart
max_rrt_time = 2

#These are reference frames for the rrt algorithm - change them to fit the world you want to plan in:
plot_region_bounds = [0,150,0,50]
world_max = [150,50]

#Number of steps in between each optimization step time (this is used to convert MILP edge weights into real valued distance.
planning_step_time = 25


##########################################################
# Replanning Variables
##########################################################


replan_req = False
replan_time = None
replan_region = None
replan_num = None
replan_cap = None

##########################################################
# Decomposition Variables
##########################################################
lambda_wt = 0.0
v_ind_wt = 0.0


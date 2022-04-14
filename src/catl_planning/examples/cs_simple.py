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
from lomap import Ts

# For creating Output File Directories, if they don't exist.
from pathlib import Path

import sys
if sys.flags.debug:
    import pdb

##########################################################
# File Names
##########################################################
ts_filename='./catl_planning/TransitionSystems/simplest_simple_farm.yaml'
save_filename = './OutputFiles/cs_simple/'
output_path = './OutputFiles/cs_simple/'

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

grave_state = 4
replan_grave = 'q4'

#Key Objectives:
#survey_map = 'F[12,36] T(3,q0,{(survey,1)}) && F[12,36] T(3,q1,{(survey,1)}) && F[12,36] T(3,q16,{(survey,1)}) && F[12,36] T(3,q17,{(survey,1)})'
#build_inf = 'F[18,44] T(20,q13,{(build,13),(survey,1)})'
#search_for_life = 'F[18,54] T(10,q3,{(R,1),(water,2)})'
#monitor_base = 'G[30,54] T(5,q13,{(Gr,2)})'
#collect_samples = 'F[0,60] T(5,q5,{(sample,1)}) && (F[0,60] T(8,q12,{(sample,1)} || F[20,60] T(3,q9,{(sample,1)})) && (F[36,60] T(3,q0,{(sample,1)} || F[0,60] T(3,q1,{(sample,1)}))&& (F[36,60] T(3,q17,{(sample,1)} || F[36,60] T(3,q16,{(sample,1)})) )'
#charge =  'G[0,60] (F[0,30] T(1,q8,{(Gr,2)} || F[0,30] T(1,q13,{(Gr,2)}))'
#formula = build_inf + ' && ' +survey_map + ' && ' + search_for_life + ' && ' + monitor_base + ' && ' + collect_samples

#easy
#formula = 'F[12,50] T(3,ZA,{(D,1)}) && F[12,44] T(3,ZB,{(D,1)}) && F[12,50] T(3,ZQ,{(su,1)}) && F[12,44] T(3,ZS,{(D,1)}) && F[10,55] T(5,ZO,{(bu,2),(su,1)}) && F[9,54] T(4,ZC,{(R,1),(wa,1)}) && G[40,54] T(5,ZO,{(Gr,2)}) && F[0,60] T(5,ZE,{(sa,1)}) && (F[0,60] T(8,ZI,{(sa,1)}) || F[20,60] T(3,ZJ,{(sa,1)})) && (F[30,60] T(3,ZH,{(sa,1)}) || F[30,60] T(3,ZK,{(sa,1)})) && (F[36,60] T(3,ZS,{(sa,1)}) || F[36,60] T(3,ZQ,{(sa,1)})) && G[0,60] (F[0,30] T(1,ZL,{(Gr,1)}) || F[0,30] T(1,ZO,{(Gr,1)}))'

#agents = [('q8', {'bu','wa','Gr'}), ('q8', {'bu','su','sa','Gr'}), ('q9', {'su','D'}),  ('q14', {'bu','su','sa','Gr'}), ('q16',{'bu','wa','Gr'}),
#              ('q14',  {'bu','sa','Gr'}), ('q15',  {'su','D'}), ('q6',  {'bu','sa','Gr'}), ('q11', {'wa','sa','su','bu','R'})]


#Harder
formula = 'G[0,50]F[0,25] T(3,blue,{(C1,1),(C2,1)}) && G[0,50]F[0,25] T(2,orange,{(C1,1),(C2,1)})'

agents = [('q2', {'C1'}), ('q2', {'C1'}),  ('q2', {'C2'}), ('q2',{'C2'})]


##########################################################
#ROS Setup
##########################################################

ros_name_index_mapping = ['create0','create1','create2','create3','create4','create5','create6','create7']
sim_2_world_converts = [-0.4, -0.1, -0.059, 0.058] #[x_off,y_off,scaley,scalex]


#Show Transition World
show_visuals = False

#Show generates a plot of all of the trajectories - It is not automatically saved
show_sol = True

#Record generates a video of the trajectories being executed in time - it is saved automatically
record_sol = False

robust = True
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
plot_region_bounds = [0,30,0,10]
world_max = [30,10]

#Number of steps in between each optimization step time (this is used to convert MILP edge weights into real valued distance.
planning_step_time = 6


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


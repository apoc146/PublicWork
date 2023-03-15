from __future__ import division
import pybullet as p
import pybullet_data
import numpy as np
import time
import argparse
import math
import os
import sys


UR5_JOINT_INDICES = [0, 1, 2]

### globals
pi=np.pi
step_size=0.05
rrt_converge_range=0.5
ITERS=2000

## joint motion ranges in radians
j0_range={"low":-2*pi,"high":2*pi}
j1_range={"low":-2*pi,"high":2*pi}
j2_range={"low":-pi,"high":pi}

def smooth_path(path, N):
    for i in range(N):
        index1 = np.random.randint(0, len(path) - 1)
        index2 = np.random.randint(0, len(path) - 1)
        
        while abs(index2 - index1) <= 1:
            index2 = np.random.randint(0, len(path) - 1)
        
        # check if there is a path between index1 and index2 by linear interpolation
        if steer_to(RRT_Node(path[index1]), RRT_Node(path[index2])):
            start = min(index1, index2)
            end = max(index1, index2)
            path = path[:start + 1] + path[end:]
    
    return path

# def can_interpolate(point1, point2):
#     #Do steer
#     pass





def set_joint_positions(body, joints, values):
    assert len(joints) == len(values)
    for joint, value in zip(joints, values):
        p.resetJointState(body, joint, value)


def draw_sphere_marker(position, radius, color):
   vs_id = p.createVisualShape(p.GEOM_SPHERE, radius=radius, rgbaColor=color)
   marker_id = p.createMultiBody(basePosition=position, baseCollisionShapeIndex=-1, baseVisualShapeIndex=vs_id)
   return marker_id


def remove_marker(marker_id):
   p.removeBody(marker_id)


def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('--birrt', action='store_true', default=False)
    parser.add_argument('--smoothing', action='store_true', default=False)
    args = parser.parse_args()
    return args

#your implementation starts here
#refer to the handout about what the these functions do and their return type
###############################################################################
class RRT_Node:
    def __init__(self, conf):
        self.conf=conf
        self.parent=None
        self.children=[]

    def set_parent(self, parent):
        self.parent=parent

    def add_child(self, child):
        self.children.append(child)

    def get_parent(self):
        return self.parent

    def get_config(self):
        return self.conf

def sample_conf():
    j0_conf=np.random.uniform(j0_range["low"],j0_range["high"])
    j1_conf=np.random.uniform(j1_range["low"],j1_range["high"])
    j2_conf=np.random.uniform(j2_range["low"],j2_range["high"])
    sample_config=np.array([j0_conf,j1_conf,j2_conf])
    # print("Sampled Config:<{}>".format(sample_config))
    
    if (sample_config==goal_conf).all():
        return sample_config,True
    return sample_config,False

def sample_conf_collision_free():
    sampled_conf,is_goal_flag=sample_conf()
    while(collision_fn(sampled_conf)==True):
        sampled_conf,is_goal_flag=sample_conf()
    return sampled_conf

def min_dist_radian(x,y):
    return np.linalg.norm(x-y)

## find the nearest node from the tree  
def find_nearest(rand_node, node_list):
    minDistance=9999999999
    nearest_node=None
    for i in range(len(node_list)):
        dist=np.linalg.norm(rand_node.conf-node_list[i].conf)
        if (dist<minDistance):
            nearest_node=node_list[i]
            minDistance=dist
    return nearest_node

## for RRT      
def steer_to(nearest_node,rand_node):
    nearest_node_conf=nearest_node.conf
    rand_node_conf=rand_node.conf

    d=np.linalg.norm(nearest_node_conf-rand_node_conf)
    steps=round(d/step_size)
    unit_step=(rand_node_conf-nearest_node_conf)/steps
    start_node_conf=nearest_node_conf
    for _ in range(1,steps):
        start_node_conf=start_node_conf+unit_step
        ## Check for collisions
        if collision_fn(start_node_conf):
            return False
    return True

def steer_to_until(nearest_node,rand_node):
    nearest_node_conf=nearest_node.conf
    rand_node_conf=rand_node.conf

    d=np.linalg.norm(nearest_node_conf-rand_node_conf)
    steps=round(d/step_size)
    unit_step=(rand_node_conf-nearest_node_conf)/steps

    preq_q_config=nearest_node.get_config()
    start_node_conf=nearest_node.get_config()

    for _ in range(1,steps):
        start_node_conf=start_node_conf+unit_step
        ## Check for collisions
        if collision_fn(start_node_conf):
            return RRT_Node(preq_q_config)
        else:
            preq_q_config=start_node_conf
    return RRT_Node(rand_node.get_config())

def poitInRadius(point,goal,range):
    print("norm diff {}".format(np.linalg.norm(point.conf-goal.conf)))
    if abs(np.linalg.norm(point.conf-goal.conf))<=range:
        return True
    return False

def RRT():
    nodes=[]
    iter_cnt=0
    
    start_node=RRT_Node(start_conf)
    goal_node=RRT_Node(goal_conf)
    nodes.append(start_node)
    
    for i in range(1,ITERS):
        iter_cnt=iter_cnt+1

        # Sample a Random Node
        sample_config,isSampledGoal=sample_conf()
        rand_node=RRT_Node(sample_config)

        if isSampledGoal==True:
            print("*** Sampled is GOAL ***")
            continue

        nearest_node=find_nearest(rand_node,nodes)

        if steer_to(nearest_node,rand_node)==True:
            # print("inside steer")
            rand_node.set_parent(nearest_node)
            nodes[nodes.index(nearest_node)].add_child(rand_node)
            nodes.append(rand_node)
            
            ## Reached Goal
            if poitInRadius(rand_node,goal_node,rrt_converge_range):
                print("********** Reached Goal ************")
                break
    
    print("Iter Count Used: {}\n".format(iter_cnt))
    print("total nodes: {}".format(len(nodes)))
    
    final_path_configs=[]
    ##Insert goal node - the last inserted node
    goal_node=nodes[-1]
    final_path_configs.append(goal_node.conf)

    ## now do back tracking from goal node to reach start node
    path_node=goal_node.get_parent()
    final_path_configs.append(path_node.conf)

    ## find the path from start to goal now
    i=0
    while True:
        i=i+1
        path_node=path_node.get_parent()
        if path_node==None:
            break
        final_path_configs.append(path_node.conf)

    print("Path len->{}".format(len(final_path_configs)))
    return final_path_configs[::-1]

def BiRRT():
    T1_nodes=[]
    T2_nodes=[]
    T1_nodes.append(RRT_Node(np.array(start_conf)))
    T2_nodes.append(RRT_Node(np.array(goal_conf)))

    T_curr,T_other=T1_nodes,T2_nodes

    for i in range(ITERS):
        # Sample a Random Node
        sample_config=sample_conf_collision_free()
        q_rand_node=RRT_Node(sample_config)
        q_nearest_node=find_nearest(q_rand_node,T_curr)
        q_s_node:RRT_Node=steer_to_until(q_nearest_node,q_rand_node)


        ## if q_s != q_nearest
        if(((q_s_node.get_config()==q_nearest_node.get_config()).all())==False):
            ## Insert this 'q_s' into the T_curr tree
            q_s_node.set_parent(q_nearest_node)
            q_nearest_node.add_child(q_s_node)
            T_curr.append(q_s_node)
            
            ## Now check for other tree
            q_bar_nearest_node=find_nearest(q_s_node,T_other)
            q_bar_s_node=steer_to_until(q_bar_nearest_node,q_s_node)

             ## if q'_s != q'_nearest
            if( (q_bar_s_node.get_config()==q_bar_nearest_node.get_config()).all()==False):
                q_bar_s_node.set_parent(q_bar_nearest_node)
                q_bar_nearest_node.add_child(q_bar_s_node)
                T_other.append(q_bar_s_node)
            
            ## if q_s == q'_s
            if((q_s_node.get_config()==q_bar_s_node.get_config()).all()==True):
                print("Solution Found\n")
                ## lets get path now

                ## Since q_node and q'_node are both same 
                ## and inserted into both you need to pop it
                
                print("TREES CURR")
                print([x.conf for x in T_curr])
                print("\n\n")
                print("TREES OTHER")
                print([x.conf for x in T_other])
                print("\n\n")

                path1=tracePath(T_curr)
                path2=tracePath(T_other)

                print("\nSUB PATH 1")
                print([x.conf for x in path1])
                print("\nSUB PATH 2")
                print([y.conf for y in path2])

                # print("QWE")
                # print(T_curr[-1].get_parent().conf)

                # print("\nASD")
                # print(T_other[-1].get_parent().conf)
                

                ## got to backtrack to recover the whole path

                ## Returns list of configs for the path
                if( (path1[0].get_config()==start_conf).all()==True):
                    # path1.reverse()
                    # path1.append(q_bar_s_node)
                    final_path=path1+path2[::-1]
                    final_path_configs=[ele.get_config() for ele in final_path]
                    return final_path_configs
                    ##pass
                
                else:
                    # path2.reverse()
                    # path2.append(q_bar_s_node)
                    final_path=path2+path1[::-1]
                    final_path_configs=[ele.get_config() for ele in final_path]
                    return final_path_configs

        if(len(T_other)<len(T_curr)):
            ## Swap Trees
            print("Start swap")
            print("before swap\n")
            print([x.conf for x in T_curr])
            print([x.conf for x in T_other])
            
            T_curr, T_other = T_other, T_curr

            print("after swap\n")
            print([x.conf for x in T_curr])
            print([x.conf for x in T_other])
            print("End swap")

def tracePath(path_list):
    ## reverse path from meet point to start/goal
    return_nodes_list=[]
    ## last node
    path_node=path_list[-1]
    return_nodes_list.append(path_node)

    ## find the path from start to goal now
    while True:
        path_node=path_node.get_parent()
        if path_node==None:
            break
        return_nodes_list.append(path_node)

    print("BiRRT Path len->{}".format(len(return_nodes_list)))
    ## Returns reversed path
    return return_nodes_list[::-1]



def BiRRT_smoothing():
    birrt_path_conf=BiRRT()
    smooth_path_conf=smooth_path(birrt_path_conf,ITERS)
    return smooth_path_conf

###############################################################################
#your implementation ends here

if __name__ == "__main__":
    args = get_args()

    # set up simulator
    physicsClient = p.connect(p.GUI)
    p.setAdditionalSearchPath(pybullet_data.getDataPath())
    p.setPhysicsEngineParameter(enableFileCaching=0)
    p.setGravity(0, 0, -9.8)
    p.configureDebugVisualizer(p.COV_ENABLE_GUI, False)
    p.configureDebugVisualizer(p.COV_ENABLE_SHADOWS, True)
    p.resetDebugVisualizerCamera(cameraDistance=1.400, cameraYaw=58.000, cameraPitch=-42.200, cameraTargetPosition=(0.0, 0.0, 0.0))

    # load objects
    plane = p.loadURDF("plane.urdf")
    ur5 = p.loadURDF('assets/ur5/ur5.urdf', basePosition=[0, 0, 0.02], useFixedBase=True)
    obstacle1 = p.loadURDF('assets/block.urdf',
                           basePosition=[1/4, 0, 1/2],
                           useFixedBase=True)
    obstacle2 = p.loadURDF('assets/block.urdf',
                           basePosition=[2/4, 0, 2/3],
                           useFixedBase=True)
    obstacles = [plane, obstacle1, obstacle2]

    # start and goal
    start_conf = (-0.813358794499552, -0.37120422397572495, -0.754454729356351)
    start_position = (0.3998897969722748, -0.3993956744670868, 0.6173484325408936)
    goal_conf = (0.7527214782907734, -0.6521867735052328, -0.4949270744967443)
    goal_position = (0.35317009687423706, 0.35294029116630554, 0.7246701717376709)
    goal_marker = draw_sphere_marker(position=goal_position, radius=0.02, color=[1, 0, 0, 1])
    set_joint_positions(ur5, UR5_JOINT_INDICES, start_conf)

    #### Converting Tuple to np.array
    start_conf=np.array(list(start_conf))
    goal_conf=np.array(list(goal_conf))
    
	# place holder to save the solution path
    path_conf = None

    # get the collision checking function
    from collision_utils import get_collision_fn
    collision_fn = get_collision_fn(ur5, UR5_JOINT_INDICES, obstacles=obstacles,
                                       attachments=[], self_collisions=True,
                                       disabled_collisions=set())

    if args.birrt:
        if args.smoothing:
            # using birrt with smoothing
            path_conf = BiRRT_smoothing()
        else:
            # using birrt without smoothing
            path_conf = BiRRT()
            print("-----Printing BIRRT PATH-----\n")
            print(path_conf)
    else:
        # using rrt
        path_conf = RRT()

    print("BiRRT Node Count")
    print(len(path_conf))
    print("after\n")

    if path_conf is None:
        # pause here
        input("no collision-free path is found within the time budget, finish?")
    else:
        #execute the path
        while True:
            for q in path_conf:
                set_joint_positions(ur5, UR5_JOINT_INDICES, q)
                time.sleep(0.5)

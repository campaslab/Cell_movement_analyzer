import numpy as np
import pandas as pd

import pos_to_vel as convert

def calc_spatial_cor(vel_time, cell_size, time):
    tags = vel_time[:,7]
    sc_val = np.empty((0,2))

    dist_matrix = np.zeros((len(tags), len(tags)))

    for ii in range(len(tags)):
        pos_dff=(vel_time[:,0]-vel_time[ii,0])**2+(vel_time[:,1]-vel_time[ii,1])**2+(vel_time[:,2]-vel_time[ii,2])**2
        pos_dff=pos_dff.astype('float')
        dist_matrix[:,ii]=(vel_time[:,0]-vel_time[ii,0])**2 + (vel_time[:,1]-vel_time[ii,1])**2 +(vel_time[:,2]-vel_time[ii,2])**2
        dist_matrix[:,ii]=np.sqrt(dist_matrix[:,ii])

    for ii in range(len(tags)):
        dis=dist_matrix[ii:,ii]
        vel_dot=vel_time[ii:,3]*vel_time[ii,3]+vel_time[ii:,4]*vel_time[ii,4]+vel_time[ii:,5]*vel_time[ii,5]
        sc_val=np.append(sc_val,np.vstack((dis,vel_dot)).T,axis=0)

    dist_bin=np.floor(np.array(sc_val[:,0]/cell_size+0.5,dtype=float))
    dis_bin_val=np.unique(dist_bin)


    sc_bin_val=np.zeros((len(dis_bin_val),4))
    for ii in range(len(dis_bin_val)):
        sc_bin_data=sc_val[dist_bin==dis_bin_val[ii]][:,1]
        sc_bin_val[ii,0]=time
        sc_bin_val[ii,1]=dis_bin_val[ii]
        sc_bin_val[ii,2]=np.mean(sc_bin_data)
        sc_bin_val[ii,3]=np.std(sc_bin_data)/np.sqrt(len(sc_bin_data))

    sc_bin_val[:,3]=sc_bin_val[:,3]/sc_bin_val[0,2]
    sc_bin_val[:,2]=sc_bin_val[:,2]/sc_bin_val[0,2]

    return sc_bin_val

def setup_spatial(filepath, cell_size, interval):
    vel_df = convert.convert_pos_to_vel(filepath, interval)
    time_points = vel_df['time'].unique()

    results=np.empty((0,4))

    for time in time_points:
        vel_time = vel_df[vel_df['time'] == time].to_numpy()
        spc_data = calc_spatial_cor(vel_time, cell_size, time)
        results=np.append(results,spc_data,axis=0)

    unique_dist = np.unique(results[:,1])
    avg_final = np.empty((0,3))

    for dist in unique_dist:
        curr_dist = results[results[:,1] == dist][:,1:]
        avg_dist = np.mean(curr_dist, axis = 0)
        avg_final = np.append(avg_final, np.array([avg_dist]), axis = 0)

    spatial_df = pd.DataFrame({'distance':avg_final[:,0], 'values':avg_final[:,1], 'error':avg_final[:,2]})

    return spatial_df

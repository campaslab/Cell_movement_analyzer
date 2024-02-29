import numpy as np
import pandas as pd

from scipy.spatial import distance_matrix

import pos_to_vel as convert

def calc_coherence(vel_time, R):
    tags = vel_time[:,7]
    C_t = np.zeros(len(tags))

    counter = 0

    dist_matrix = np.zeros((len(tags), len(tags)))

    for ii in range(len(tags)):
        pos_dff=(vel_time[:,0]-vel_time[ii,0])**2+(vel_time[:,1]-vel_time[ii,1])**2+(vel_time[:,2]-vel_time[ii,2])**2
        pos_dff=pos_dff.astype('float')
        dist_matrix[:,ii]=(vel_time[:,0]-vel_time[ii,0])**2 + (vel_time[:,1]-vel_time[ii,1])**2 +(vel_time[:,2]-vel_time[ii,2])**2
        dist_matrix[:,ii]=np.sqrt(dist_matrix[:,ii])

    for ii in range(len(tags)):
        distances = dist_matrix[:,ii]
        neighbor_tags = np.transpose(np.argwhere(distances < R))

        vel_values = vel_time[neighbor_tags,3:6][0]
        vel_values = vel_values.astype('float')

        # check whether the magnitude of velocity is equal to zero
        # exclude cells with zero velocity
        vel_values = vel_values[(vel_values[:,0] != 0) | (vel_values[:,1] != 0) | (vel_values[:,2] != 0)]

        # if there's nothing after filtering out zero velocities, move on to the next cell
        if len(vel_values) == 0:
            continue

        vel_norm = np.linalg.norm(vel_values, axis = 1)

        normalized = vel_values / vel_norm[:,None]
        norm_sum = np.sum(normalized, axis = 0)

        C_t[counter] = np.linalg.norm(norm_sum) / len(vel_values)
        counter += 1

    return np.mean(C_t), np.std(C_t), len(C_t)

def setup_coherence(filepath, cell_size, interval):
    vel_df = convert.convert_pos_to_vel(filepath, interval)

    C_t_mean = []
    C_t_std = []
    C_t_n = []
    R = cell_size * 1.5

    time_points = vel_df['time'].unique()

    for time in time_points:
        vel_time = vel_df[vel_df['time'] == time].to_numpy()

        mean, std, n = calc_coherence(vel_time, R)
        C_t_mean.append(mean)
        C_t_std.append(std)
        C_t_n.append(n)

    time = time_points * interval
    time = time - time[0]

    error = np.nan_to_num(C_t_std / np.sqrt(C_t_n))

    coherence_df = pd.DataFrame({'time':time, 'mean':C_t_mean, 'error':error})

    return coherence_df

import pandas as pd
import numpy as np
import itertools

import pos_to_vel as convert

def get_indicies(max_time):
    combinations = []
    for tm in range(max_time):
        t = list(np.arange(max_time - tm))
        tau = list(np.arange(tm, max_time))
        combinations.append(list(map(lambda x, y:(tm,x,y), t, tau)))
    return list(itertools.chain(*combinations))

def calc_vel_auto(vel_data, curr_tag):
    cell_data = vel_data[vel_data['tag'] == curr_tag]

    vel = np.transpose(cell_data[['vx', 'vy', 'vz']].to_numpy())

    indicies = get_indicies(vel.shape[1])

    dot_products = np.empty((len(indicies), 2))
    iterator = 0
    for index in indicies:
        tm = index[0]
        t_index = index[1]
        tau_index = index[2]
        result = np.array([tm, np.dot(vel[:,t_index], vel[:,tau_index])])
        dot_products[iterator,:] = result
        iterator += 1

    return dot_products

def setup_vel_auto(filepath, interval):
    vel_df = convert.convert_pos_to_vel(filepath, interval)
    all_cells = vel_df['tag'].unique()
    auto_data_all = np.empty((0,2))

    for tag in all_cells:
        auto_v_result = calc_vel_auto(vel_df, tag)
        auto_data_all = np.append(auto_data_all, auto_v_result, axis = 0)

    time_diff = np.unique(auto_data_all[:,0])

    auto_cor_val = []
    auto_cor_error = []

    for time in time_diff:
        values = auto_data_all[auto_data_all[:,0] == time, 1]
        auto_cor_val = np.append(auto_cor_val, np.mean(values))
        auto_cor_error = np.append(auto_cor_error, np.std(values) / np.sqrt(len(values)))

    auto_cor_error = auto_cor_error / auto_cor_val[0]
    auto_cor_val = auto_cor_val / auto_cor_val[0]

    time_diff = time_diff * interval

    vel_auto_df = pd.DataFrame({'time diff':time_diff, 'values':auto_cor_val, 'error':auto_cor_error})

    return vel_auto_df

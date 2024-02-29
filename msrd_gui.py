import numpy as np
import pandas as pd

def find_closest_neighbor(curr_tag, pos_data):
    current_cell = pos_data[pos_data['tag'] == curr_tag]
    first_time = current_cell['time'].iloc[0]
    pos_neighbors = pos_data[(pos_data['time'] == first_time) & (pos_data['tag'] != curr_tag)]
    x_curr = current_cell['x'].iloc[0]
    y_curr = current_cell['y'].iloc[0]
    z_curr = current_cell['z'].iloc[0]
    pos_neighbors['distance'] = np.sqrt((x_curr - pos_neighbors['x']) ** 2 + (y_curr - pos_neighbors['y']) ** 2 + (z_curr - pos_neighbors['z']) ** 2)
    closest_tag = int(pos_neighbors.sort_values('distance').iloc[0]['tag'])
    return closest_tag

def calc_msrd(curr_tag, pos_data):
    neighbor_tag = find_closest_neighbor(curr_tag, pos_data)
    pre_current_time = pos_data[pos_data['tag'] == curr_tag]['time'].iloc[0]
    pre_neighbor_time = pos_data[pos_data['tag'] == neighbor_tag]['time'].iloc[0]
    start = 0
    if (pre_current_time != pre_neighbor_time):
        start = max(pre_current_time, pre_neighbor_time)
    current_cell = pos_data[(pos_data['tag'] == curr_tag) & (pos_data['time'] >= start)][['x', 'y', 'z']].values
    neighbor_cell = pos_data[(pos_data['tag'] == neighbor_tag) & (pos_data['time'] >= start)][['x', 'y', 'z']].values
    r_x0 = current_cell[0][0] - neighbor_cell[0][0]
    r_y0 = current_cell[0][1] - neighbor_cell[0][1]
    r_z0 = current_cell[0][2] - neighbor_cell[0][2]
    max_time = min(len(current_cell), len(neighbor_cell))
    result = (current_cell[:max_time,0] - neighbor_cell[:max_time,0] - r_x0) ** 2 + (current_cell[:max_time,1] - neighbor_cell[:max_time,1] - r_y0) ** 2 + (current_cell[:max_time,2] - neighbor_cell[:max_time,2] - r_z0) ** 2
    return result

def aggregate_msrd(all_cells, pos_data, time_points):
    msrd_all = np.empty((0, time_points))
    visited = {}
    for curr in all_cells:
        visited[curr] = False
    for curr in all_cells:
        neighbor = find_closest_neighbor(curr, pos_data)
        if not (visited[curr] and visited[neighbor]):
            curr_result = calc_msrd(curr, pos_data)
            if len(curr_result) < time_points:
                curr_result = np.append(curr_result, np.repeat(np.nan, time_points - len(curr_result)))
            msrd_all = np.append(msrd_all, [curr_result], axis = 0)
            visited[neighbor] = True
            visited[curr] = True
    return msrd_all

def setup_msrd(pos_filename, time_interval, cell_size): # add an interval parameter for time and cell size parameter for normalization
    position_data = pd.read_csv(str(pos_filename), usecols = [0, 1, 2, 6, 7], names = ['x', 'y', 'z', 'time', 'tag'], skiprows = 4, float_precision = 'round_trip')
    time_points = len(position_data['time'].unique())
    all_cells = position_data['tag'].unique()
    MSRD_result = aggregate_msrd(all_cells, position_data, time_points)
    mean = np.nanmean(MSRD_result, axis = 0)
    std = np.nanstd(MSRD_result, axis = 0)
    total = np.nansum(MSRD_result, axis = 0)
    n = np.nan_to_num(total/mean)
    n[0] = n[1]
    sqrtn = np.sqrt(n)
    error = np.nan_to_num(std/sqrtn)
    msrd_final = np.empty((time_points, 4))
    for ti in range(time_points):
        msrd_final[ti,0] = ti * time_interval
        msrd_final[ti,1] = mean[ti] / cell_size
        msrd_final[ti,2] = error[ti] / cell_size
        msrd_final[ti,3] = n[ti]

    msrd_df = pd.DataFrame(data = msrd_final, columns = ['time', 'MSRD', 'error', 'N'])
    return msrd_df

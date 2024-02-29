import pandas as pd
import numpy as np

def calc_velocity(positions, delta_t):
    delta_x = positions[2:] - positions[:len(positions) - 2]
    velocity = delta_x / (2 * delta_t)
    first_vel = (positions[1] - positions[0]) / delta_t
    last_vel = (positions[len(positions)-1] - positions[len(positions)-2]) / delta_t
    velocity = np.insert(velocity, 0, first_vel)
    velocity = np.append(velocity, last_vel)
    return velocity

def convert_pos_to_vel(pos_filepath, time_interval):
    pos_df = pd.read_csv(pos_filepath, usecols = [0, 1, 2, 6, 7], names = ['x', 'y', 'z', 'time', 'tag'], skiprows = 4, float_precision = 'round_trip')
    delta_t = time_interval

    time_points = pos_df['time'].unique()
    tags = pos_df['tag'].unique()

    velocity_df = pd.DataFrame(columns = ['x', 'y', 'z', 'vx', 'vy', 'vz', 'time', 'tag'])

    for tag in tags:
        x_vel = pos_df[pos_df['tag'] == tag]['x'].to_numpy()
        y_vel = pos_df[pos_df['tag'] == tag]['y'].to_numpy()
        z_vel = pos_df[pos_df['tag'] == tag]['z'].to_numpy()
        vx_vel = calc_velocity(x_vel, delta_t)
        vy_vel = calc_velocity(y_vel, delta_t)
        vz_vel = calc_velocity(z_vel, delta_t)
        time_points = pos_df[pos_df['tag'] == tag]['time'].to_numpy()
        data = {'x':x_vel, 'y':y_vel, 'z':z_vel, 'vx':vx_vel, 'vy':vy_vel, 'vz':vz_vel, 'time':time_points, 'tag':tag}
        velocity_df = velocity_df.append(pd.DataFrame(data))

    return velocity_df

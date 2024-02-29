import numpy as np
import pandas as pd

import pos_to_vel as convert

def setup_speed(filepath, interval):
    vel_df = convert.convert_pos_to_vel(filepath, interval).drop(columns = ['x', 'y', 'z', 'tag'])
    vel_df['speed'] = np.sqrt(np.square(vel_df.drop(columns = ['time'])).sum(axis=1))

    avg_vel = vel_df.groupby('time').mean().reset_index(level = ['time'])

    avg_norm = avg_vel
    avg_norm['avg vel'] = np.sqrt(np.square(avg_vel.drop(columns = ['time', 'speed'])).sum(axis = 1))
    avg_norm['avg norm vel'] = avg_norm['avg vel'] / avg_norm['speed']

    avg_norm = avg_norm.drop(columns = ['speed', 'avg vel', 'vx', 'vy', 'vz'])
    avg_norm['time'] = avg_norm['time'] * interval
    avg_norm['error'] = 0

    return avg_norm

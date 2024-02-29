import os
import shutil

import pandas as pd
import numpy as np

global result_folders
result_folders = {'MSRD RESULT', 'VEL AUTO RESULT', 'COHER RESULT', 'SPATIAL ABS RESULT', 'SPATIAL REL RESULT', 'AVG NORM VEL RESULT'}

def parse_directory(directory):
    # get all the subfolders under the root directory
    # filtering out any hidden directories like .DS_Store
    subfolders = [dir for dir in os.listdir(directory) if not dir.startswith('.')]

    # filepath is the key while what directory is in as the value
    file_folder = {}

    # dictionary to store subfolder to dictionary of types of results to count
    result_counts = {}
    for result in result_folders:
        result_counts[result] = 0

    # dictionary to keep track of total number of files
    num_files = 0

    # get the filepaths of each subfolder along with possible counts of results
    for folder in subfolders:
        filepaths, counts = filter_results(directory, folder)

        # populate the filepath dictionary
        for filepath in filepaths:
            file_folder[filepath] = folder

        # update the results counter
        for result in result_folders:
            result_counts[result] += counts[result]

        num_files += len(filepaths)

    return file_folder, subfolders, result_counts, num_files

def filter_results(root_path, subdirectory):
    # get the contents in the subdirectory
    contents = {content for content in os.listdir(root_path + "/" + subdirectory) if not content.startswith('.')}

    # see if the subdirectory exist any result folders
    intersect = contents & result_folders
    result_count = {}

    for name in result_folders:
        result_count[name] = 0

    # if it exists, count the number of results that exist
    if (len(intersect) > 0):
        for name in intersect:
            result_count[name] = count_results(root_path + "/" + subdirectory + "/" + name)

    # remove any result folders if there are any
    input_files = contents - result_folders

    # create a list of file paths
    filepaths = []
    for file in input_files:
        filepaths.append(root_path + "/" + subdirectory + "/" + file)

    return filepaths, result_count

def count_results(result_path):
    result_files = [result for result in os.listdir(result_path) if not result.startswith('.')]
    return len(result_files)

def create_result_folders(root_path, subfolders, type):
    result_name = ""

    if type == "Mean Squared Relative Displacement":
        result_name = 'MSRD RESULT'
    elif type == "Velocity Temporal Autocorrelation":
        result_name = 'VEL AUTO RESULT'
    elif type == "Coherence":
        result_name = 'COHER RESULT'
    elif type == "Average Normalized Velocity":
        result_name = 'AVG NORM VEL RESULT'
    elif type == "Velocity Spatial Correlation (Relative)":
        result_name = 'SPATIAL REL RESULT'
    else:
        result_name = 'SPATIAL ABS RESULT'

    for folder in subfolders:
        dir_path = root_path + "/" + folder + "/" + result_name
        # if a result folder already exists, we are going to delete it and recreate an empty one
        if (os.path.exists(dir_path)):
            shutil.rmtree(dir_path)
        os.mkdir(dir_path)

def create_result_file(root_path, subfolder, result_folder, input_filepath, result_df):
    tail = os.path.basename(input_filepath)
    filename, _ = os.path.splitext(tail)
    result_filename = root_path + "/" + subfolder + "/" + result_folder + "/" + filename + "_RESULT.csv"
    result_df.to_csv(result_filename, index = False)

def get_results(root_path, subfolders, type):
    result_name = ""

    if type == "Mean Squared Relative Displacement":
        result_name = 'MSRD RESULT'
    elif type == "Velocity Temporal Autocorrelation":
        result_name = 'VEL AUTO RESULT'
    elif type == "Coherence":
        result_name = 'COHER RESULT'
    elif type == "Average Normalized Velocity":
        result_name = 'AVG NORM VEL RESULT'
    elif type == "Velocity Spatial Correlation (Relative)":
        result_name = 'SPATIAL REL RESULT'
    else:
        result_name = 'SPATIAL ABS RESULT'

    # need to acccess of the specific result folder for each subfolder
    # need to check which folders contains result folders
    folder_with_results = []
    for folder in subfolders:
        dir_path = root_path + "/" + folder + "/" + result_name
        if os.path.exists(dir_path):
            folder_with_results.append(folder)

    # need to keep track of the time with the fewest elements
    min_time_points = {}

    # get the result files in those folders (files that end in _RESULT.csv)

    # store result filepath to its subfolder in a dictionary
    results_folder = {}

    for folder in folder_with_results:
        result_path = root_path + "/" + folder + "/" + result_name
        result_files = [result_path + "/" + result for result in os.listdir(result_path) if result.endswith('_RESULT.csv')]
        for filepath in result_files:
            results_folder[filepath] = folder
        min_time_points[folder] = []

    # create a list of results in a tuple (time, val, err, folder)
    results = []

    for filepath in results_folder:
        # time is column 0, val is column 1, err is column 2
        df = pd.read_csv(filepath).to_numpy()
        time = df[:,0]
        val = df[:,1]
        err = df[:,2]

        # assume distances is interval of 1

        num_nonzero = np.count_nonzero(~np.isnan(val))
        time_diff = (time[1] - time[0])

        if num_nonzero < len(min_time_points[results_folder[filepath]]) or len(min_time_points[results_folder[filepath]]) == 0:
            time_range = np.arange(0, num_nonzero, 1) * time_diff
            min_time_points[results_folder[filepath]] = time_range

        results.append((time, val, err, results_folder[filepath]))

    return results, min_time_points

def compute_avg_results(root_path, subfolders, functions):
    # collect results of each directory
    # functions = ["Mean Squared Relative Displacement", "Velocity Temporal Autocorrelation", "Velocity Spatial Correlation (Absolute)", "Velocity Spatial Correlation (Relative)", "Average Normalized Velocity"]

    for func in functions:
        results, min_times = get_results(root_path, subfolders, func)

        val_avg = {}
        err_avg = {}

        for dir in min_times:
            val_avg[dir] = np.empty((0, len(min_times[dir])))
            err_avg[dir] = np.empty((0, len(min_times[dir])))

        for result in results:
            time = result[0]
            val = result[1]
            err = result[2]
            folder = result[3]

            if len(val) > len(min_times[folder]):
                val = np.array([val[0:len(min_times[folder])]])
                err = np.array([err[0:len(min_times[folder])]])
            else:
                val = np.array([val])
                err = np.array([err])

            val_avg[folder] = np.concatenate((val_avg[folder], val), axis = 0)
            err_avg[folder] = np.concatenate((err_avg[folder], err), axis = 0)

        for dir in min_times:
            avg = np.nanmean(val_avg[dir], axis = 0)
            err = None
            if func == "Average Normalized Velocity":
                err = np.nanstd(val_avg[dir], axis = 0)
            else:
                err = np.nanmean(err_avg[dir], axis = 0)
            final_time = min_times[dir]

            # write the result in the respective folder
            # avg_df = None
            if func == "Mean Squared Relative Displacement":
                avg_df = pd.DataFrame({'Time (min)': final_time, 'MSRD Avg': avg, 'MSRD Avg Err': err})
                result_filename = root_path + "/" + dir + "/MSRD RESULT/MSRD_AVG_RESULT.csv"
                avg_df.to_csv(result_filename, index = False)
            elif func == "Velocity Temporal Autocorrelation":
                avg_df = pd.DataFrame({'Time (min)': final_time, 'Vel Auto Avg': avg, 'Vel Auto Avg Err': err})
                result_filename = root_path + "/" + dir + "/VEL AUTO RESULT/VEL_AUTO_AVG_RESULT.csv"
                avg_df.to_csv(result_filename, index = False)
            elif func == "Velocity Spatial Correlation (Relative)":
                avg_df = pd.DataFrame({'Dist / Cell Size': final_time, 'Spatial Rel Avg': avg, 'Spatial Rel Avg Err': err})
                result_filename = root_path + "/" + dir + "/SPATIAL REL RESULT/SPATIAL_REL_AVG_RESULT.csv"
                avg_df.to_csv(result_filename, index = False)
            elif func == "Velocity Spatial Correlation (Absolute)":
                avg_df = pd.DataFrame({'Dist / Cell Size': final_time, 'Spatial Abs Avg': avg, 'Spatial Abs Avg Err': err})
                result_filename = root_path + "/" + dir + "/SPATIAL ABS RESULT/SPATIAL_ABS_AVG_RESULT.csv"
                avg_df.to_csv(result_filename, index = False)
            else:
                avg_df = pd.DataFrame({'Time (min)': final_time, 'Avg Norm Vel Avg': avg, 'Avg Norm Vel Avg Err': err})
                result_filename = root_path + "/" + dir + "/AVG NORM VEL RESULT/AVG_NORM_VEL_AVG_RESULT.csv"
                avg_df.to_csv(result_filename, index = False)

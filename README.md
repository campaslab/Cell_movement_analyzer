# Cell-Tracking-GUI

This version of the GUI does the following things:
- calculates Mean Squared Relative Displacement, Velocity Autocorrelation, Velocity Spatial Correlation, and Mean Speed
- Coherence is attached in the backend but not accessable in the front end
- plots the result along with the average of each subdirectory
- output the results in its designated folder
- output the averaged results as well
- data can be reloaded to be plotted if calculated already
- this version assumes that all the input data is position

**System requirements**

Users need to install Python 3 and the necessary libraries to run the cell movement analyzer. The required libraries are NumPy and Pandas. The software is standalone and does not require any additional external software to run. It has been tested exclusively on macOS version 12 and later, so compatibility with Microsoft Windows has not been verified. No non-standard hardware is required to use the software.

**Installation guide**

No additional installation steps are required to run the cell movement analyzer. 

**Demos**

Synthetic data files for demos and final outcomes are included in the repository under the folders /demos/data_files/ and /demos/outcomes/, respectively. Instructions for running the analysis on the data are provided in the user guide, "cell_movement_analyzer_user_guide.pdf." The entire analysis on the synthetic data should be completed within a few minutes on a typical personal computer.

**Instructions for use**

Instructions for running the analysis are provided in the user guide. For more detail, please refer to the user guide, "cell_movement_analyzer_user_guide.pdf"

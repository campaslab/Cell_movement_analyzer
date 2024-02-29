import os, sys
import numpy as np
import pandas as pd

import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar

from PyQt5 import QtGui, QtCore, QtWidgets
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *

import warnings

from functools import partial

import file_traversal as file_sys
import msrd_gui as msrd
import vel_auto_gui as vel_auto
import coherence_gui as coher
import spatial_auto_gui as spatial
import spatial_cor_orig as spatial_cor
import mean_speed_gui as speed

class Widget(QWidget):
    def __init__(self):
        super(Widget, self).__init__()
        self.home()

    def center(self):
        qr = self.frameGeometry()
        cp = QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())

    def home(self):
        # creation of the window
        self.setGeometry(1000, 1000, 1000, 1000)
        self.setWindowTitle("Cell Tracking Calculations")
        self.center()

        # following a grid format of adding the widgets
        grid = QGridLayout()
        self.setLayout(grid)

        # setting up the plot window
        self.figure = plt.figure(figsize = (15, 5))
        self.canvas = FigureCanvas(self.figure)
        self.toolbar = NavigationToolbar(self.canvas, self)
        grid.addWidget(self.canvas, 8, 0, 1, 3)
        grid.addWidget(self.toolbar, 7, 0, 1, 3)

        # button to get the data from user
        btn1 = QPushButton("Import CSV", self)
        btn1.resize(btn1.sizeHint())
        btn1.clicked.connect(self.get_data)
        grid.addWidget(btn1, 0, 0)

        # list of computations the program can do
        self.functions = ["Mean Squared Relative Displacement", "Velocity Temporal Autocorrelation", "Velocity Spatial Correlation (Absolute)", "Velocity Spatial Correlation (Relative)", "Average Normalized Velocity"]

        # store the QLabels for each computation
        self.progress_texts = {}
        pos = 1 # position where to begin adding the information for each computation
        spaces = " " * 5 # default spaces set for MSRD formatting

        # for formatting MSRD is the longest word, so the others need to add more spaces
        str_length = len(self.functions[2])

        # extra spacing due to weird grid formatting
        extra = 0

        self.num_spaces = {self.functions[0]: 5, self.functions[1]: 10,
                           self.functions[2]: 4, self.functions[3]: 5,
                           self.functions[4]: 19}

        for func in self.functions:
            spaces = " " * self.num_spaces[func]
            label = func + ":" + spaces + " 0 / 0   Analyzed"
            self.progress_texts[func] = QLabel(label)
            grid.addWidget(self.progress_texts[func], pos, 0, 1, 1)
            pos += 1


        # plot choices
        # all the choices will be buttons since only one plot can be shown on the window
        grid.addWidget(QLabel("Choose what to plot:"), 0, 2)

        btn2 = QPushButton(self.functions[0], self)
        btn2.resize(btn2.sizeHint())
        grid.addWidget(btn2, 1, 2)
        btn2.clicked.connect(partial(self.plot, func = self.functions[0]))

        btn3 = QPushButton(self.functions[1], self)
        btn3.resize(btn3.sizeHint())
        grid.addWidget(btn3, 2, 2)
        btn3.clicked.connect(partial(self.plot, func = self.functions[1]))

        btn4 = QPushButton(self.functions[2], self)
        btn4.resize(btn4.sizeHint())
        grid.addWidget(btn4, 3, 2)
        btn4.clicked.connect(partial(self.plot, func = self.functions[2]))

        btn6 = QPushButton(self.functions[3], self)
        btn6.resize(btn6.sizeHint())
        grid.addWidget(btn6, 4, 2)
        btn6.clicked.connect(partial(self.plot, func = self.functions[3]))

        btn7 = QPushButton(self.functions[4], self)
        btn7.resize(btn7.sizeHint())
        grid.addWidget(btn7, 5, 2)
        btn7.clicked.connect(partial(self.plot, func = self.functions[4]))

        # computation choices
        choices = QLabel("Choose what to calculate: ")
        grid.addWidget(choices, 0, 1)

        # can't assign with self.functions due to class instances
        # the checkbox is writing over the string list
        self.list_checkbox = ["Mean Squared Relative Displacement", "Velocity Temporal Autocorrelation", "Velocity Spatial Correlation (Absolute)", "Velocity Spatial Correlation (Relative)", "Average Normalized Velocity"]

        for i, v in enumerate(self.list_checkbox):
            self.list_checkbox[i] = QCheckBox(v)
            grid.addWidget(self.list_checkbox[i], i + 1, 1)

        btn5 = QPushButton("Analyze", self)
        btn5.resize(btn5.sizeHint())
        grid.addWidget(btn5, 6, 1)
        btn5.clicked.connect(self.checkbox_changed)

        # initialize some variables
        self.root_path = ""

        self.show()

    def update_tracker(self, func, count, total):
        spaces = " " * self.num_spaces[func]
        self.progress_texts[func].setText(func + ":" + spaces + " %s / %s   Analyzed" % (count, total))

    def get_data(self):
        self.root_path = QFileDialog.getExistingDirectory(self, "Select Root Folder")

        if self.root_path == "":
            # add a pop up window saying nothing was imported
            msg = QMessageBox()
            msg.setWindowTitle("Import CSV Warning")
            msg.setText("Nothing was selected to be imported.")
            msg.setIcon(QMessageBox.Information)
            msg.exec_()

        else:
            # pass into the file traversal function
            self.file_directory, self.directories, self.num_analyzed, self.total_files = file_sys.parse_directory(self.root_path)

            # update the progress texts
            for func in self.num_analyzed:
                if func == "MSRD RESULT":
                    self.update_tracker(self.functions[0], self.num_analyzed[func], self.total_files)
                elif func == "VEL AUTO RESULT":
                    self.update_tracker(self.functions[1], self.num_analyzed[func], self.total_files)
                elif func == "SPATIAL REL RESULT":
                    self.update_tracker(self.functions[3], self.num_analyzed[func], self.total_files)
                elif func == "SPATIAL ABS RESULT":
                    self.update_tracker(self.functions[2], self.num_analyzed[func], self.total_files)
                elif func == "AVG NORM VEL RESULT":
                    self.update_tracker(self.functions[4], self.num_analyzed[func], self.total_files)

            QCoreApplication.processEvents()

    def get_parameters(self): # TODO: handle invalid input
        # get the interval between time points
        self.interval = -1
        self.cell_size = -1

        interval, okPressed = QInputDialog.getDouble(self, "Time Interval Input", "Time Interval (in min): ", 1, 0, 100, 5)
        if okPressed:
            self.interval = interval

            # get the cell size
            size, okPressed = QInputDialog.getDouble(self, "Cell Size Input", "Cell Size (in um): ", 1, 0, 100, 5)
            if okPressed:
                self.cell_size = size

    def checkbox_changed(self):
        # if nothing was imported, pop up window and skip all of the info gathering
        if self.root_path == "":
            msg = QMessageBox()
            msg.setWindowTitle("Computation Error")
            msg.setText("No data was imported. Computation cannot be done.")
            msg.setIcon(QMessageBox.Critical)
            msg.exec_()
        else:
            # ask for the parameters first and then iterate through the selection
            self.get_parameters()
            # maybe check the valid parameters here before continuing the calculation
            # pop up window if invalid parameters
            selected = []
            if not (self.interval == -1 and self.cell_size == -1):
                if self.interval <= 0 or self.cell_size <= 0:
                    msg = QMessageBox()
                    msg.setWindowTitle("Invalid Input")
                    msg.setText("Interval and Cell Size input has to be nonzero. Computation cannot be done.")
                    msg.setIcon(QMessageBox.Critical)
                    msg.exec_()
                else:
                    # iterate through the selection
                    for i, v in enumerate(self.list_checkbox):
                        if v.checkState():
                            if i == 0:
                                self.calculate(self.functions[0])
                                selected.append(self.functions[0])
                            elif i == 1:
                                self.calculate(self.functions[1])
                                selected.append(self.functions[1])
                            elif i == 2:
                                self.calculate(self.functions[2])
                                selected.append(self.functions[2])
                            elif i == 3:
                                self.calculate(self.functions[3])
                                selected.append(self.functions[3])
                            elif i == 4:
                                self.calculate(self.functions[4])
                                selected.append(self.functions[4])
                    # calculate averages
                    print(selected)
                    file_sys.compute_avg_results(self.root_path, self.directories, selected)
                    # print computation is done
                    msg = QMessageBox()
                    msg.setWindowTitle("Computation Done")
                    msg.setText("All files have been analyzed!")
                    msg.setIcon(QMessageBox.Information)
                    msg.exec_()

    def calculate(self, func):
        # need to update the counter as zero
        self.update_tracker(func, 0, self.total_files)
        QCoreApplication.processEvents()

        # computes the items and save them into the results folder
        # print("about to create result folders for " + func)
        # create the directories in each subfolder
        file_sys.create_result_folders(self.root_path, self.directories, func)

        # currently, we are going to rewrite over the results, so counter starts at 1
        counter = 1

        # computation
        for filepath in self.file_directory:
            if func == self.functions[0]:
                result = msrd.setup_msrd(filepath, self.interval, self.cell_size ** 2)

                # write the result into a result file
                file_sys.create_result_file(self.root_path, self.file_directory[filepath], 'MSRD RESULT', filepath, result)

                # update counter
                self.update_tracker(func, counter, self.total_files)

            elif func == self.functions[1]:
                result = vel_auto.setup_vel_auto(filepath, self.interval)
                file_sys.create_result_file(self.root_path, self.file_directory[filepath], 'VEL AUTO RESULT', filepath, result)
                self.update_tracker(func, counter, self.total_files)

            elif func == self.functions[3]:
                result = spatial.setup_spatial(filepath, self.cell_size, self.interval)
                file_sys.create_result_file(self.root_path, self.file_directory[filepath], 'SPATIAL REL RESULT', filepath, result)
                self.update_tracker(func, counter, self.total_files)

            elif func == self.functions[2]:
                result = spatial_cor.setup_spatial(filepath, self.cell_size, self.interval)
                file_sys.create_result_file(self.root_path, self.file_directory[filepath], 'SPATIAL ABS RESULT', filepath, result)
                self.update_tracker(func, counter, self.total_files)

            elif func == self.functions[4]:
                result = speed.setup_speed(filepath, self.interval)
                file_sys.create_result_file(self.root_path, self.file_directory[filepath], 'AVG NORM VEL RESULT', filepath, result)
                self.update_tracker(func, counter, self.total_files)

            counter += 1
            QCoreApplication.processEvents()

    def plot(self, func):
        plt.cla()
        ax = self.figure.add_subplot(111)

        # error checking in plotting
        if self.root_path == "":
            msg = QMessageBox()
            msg.setWindowTitle("Plotting Error")
            msg.setText("No data was imported. Plotting cannot be done.")
            msg.setIcon(QMessageBox.Critical)
            msg.exec_()
        else:

            # get the results from the results folder
            # return a list containing tuples of (time, val, err, dir)
            # also return directories with their min time
            # get the time interval in minutes as well
            results, min_times = file_sys.get_results(self.root_path, self.directories, func)
            # set up averages of values and errors
            val_avg = {}
            err_avg = {}

            for dir in min_times:
                val_avg[dir] = np.empty((0, len(min_times[dir])))
                err_avg[dir] = np.empty((0, len(min_times[dir])))

            # get the index of the file's directory from the directory list to associate which color it is
            colors = ['b', 'g', 'r', 'c', 'm', 'y', 'k', 'w']

            # plotting individuals
            for result in results:
                if func == self.functions[2] or func == self.functions[3]:
                    time = result[0] # spatial is dist not time
                else:
                    time = result[0]
                val = result[1]
                err = result[2]

                folder = result[3]

                color_choice = self.directories.index(folder) % len(colors)
                plt.errorbar(time, val, err, fmt = colors[color_choice], alpha = 0.1)

                if len(val) > len(min_times[folder]):
                    val = np.array([val[0:len(min_times[folder])]])
                    err = np.array([err[0:len(min_times[folder])]])
                else:
                    val = np.array([val])
                    err = np.array([err])

                val_avg[folder] = np.concatenate((val_avg[folder], val), axis = 0)
                err_avg[folder] = np.concatenate((err_avg[folder], err), axis = 0)

            # plotting average
            for dir in min_times:
                val_avg[dir] = np.nanmean(val_avg[dir], axis = 0)
                if func == self.functions[4]:
                    err_avg[dir] = np.nanstd(val_avg[dir], axis = 0)
                else:
                    err_avg[dir] = np.nanmean(err_avg[dir], axis = 0)
                color_choice = self.directories.index(dir) % len(colors)
                if func == self.functions[2] or func == self.functions[3]: # no need for conversion for distance
                    final_time = min_times[dir]
                else:
                    final_time = min_times[dir]
                plt.errorbar(final_time, val_avg[dir], err_avg[dir], label = dir, fmt = colors[color_choice])

            if func == self.functions[0]:
                plt.xlabel('Time (min)')
                plt.ylabel('Mean Squared Relative Displacement Value')
                ax.set_title('Mean Squared Relative Displacement')
            elif func == self.functions[1]:
                plt.xlabel('Time Difference (min)')
                plt.ylabel('Temporal Correlation Value')
                ax.set_title('Velocity Temporal Autocorrelation')
            elif func == self.functions[3]:
                plt.ylabel('Spatial Correlation Value')
                plt.xlabel('Distance / Cell Size')
                ax.set_title('Velocity Spatial Correlation (Relative)')
            elif func == self.functions[2]:
                plt.ylabel('Spatial Correlation Value')
                plt.xlabel('Distance / Cell Size')
                ax.set_title('Velocity Spatial Correlation (Absolute)')
            else:
                plt.ylabel('Average Normalized Velocity Value')
                plt.xlabel('Time (min)')
                ax.set_title('Average Normalized Velocity')

            plt.legend(loc = 0)
            plt.grid()

            self.canvas.draw()


def handler(msg_type, msg_log_context, msg_string):
    pass

# wrapper function to run the GUI
def run():
    qInstallMessageHandler(handler)
    warnings.filterwarnings("ignore")
    app = QApplication(sys.argv)
    GUI = Widget()
    sys.exit(app.exec_())

run()

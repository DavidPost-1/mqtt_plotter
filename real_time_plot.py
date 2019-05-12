#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun May 12 00:27:20 2019

@author: dave
"""

import sys
import numpy as np
import multiprocessing
import paho.mqtt.client as mqtt
import PyQt5.QtWidgets as qt
from PyQt5.QtCore import QObject, pyqtSignal, QThread
from matplotlib.backends.backend_qt5agg import (
        FigureCanvas, NavigationToolbar2QT as NavigationToolbar)
from matplotlib.figure import Figure
import numpy as np


class gui(qt.QWidget):
    def __init__(self, data_queue):
        super().__init__()
        self.data = np.array([])
        self.data_queue = data_queue
        self.MyUi()

        def on_connect(client, userdata, flags, rc):
            '''
            Callback function to run after connecting to an MQTT server.'''
            print("Connected with result code "+str(rc))

            # Subscribe
            print(self.input_mqtttopic.text())
            client.subscribe(self.input_mqtttopic.text())

            # Buttons etc
            self.button_connect.clicked.disconnect()
            self.button_connect.clicked.connect(self.disconnect)
            self.button_connect.setText("Disconnect")

            self.input_mqttport.setEnabled(False)
            self.input_mqttserver.setEnabled(False)
            self.input_mqtttopic.setEnabled(False)



        def on_message(client, userdata, msg):
            '''
            Callback function to run after a message is recieved from the MQTT
            server.
            '''
            print(msg.topic+" "+str(msg.payload))
            #print(self.data)
            self.update_plot(float(msg.payload))


        def on_disconnect(client, userdata, rc):
            if rc != 0:
                print("Unexpected disconnection")
            else:
                print("Disconnected")

            self.button_connect.clicked.disconnect()
            self.button_connect.clicked.connect(self.connect)
            self.button_connect.setText("Connect")

            self.input_mqttport.setEnabled(True)
            self.input_mqttserver.setEnabled(True)
            self.input_mqtttopic.setEnabled(True)


        self.client = mqtt.Client()
        self.client.on_connect = on_connect
        self.client.on_message = on_message
        self.client.on_disconnect = on_disconnect
        self.button_connect.clicked.connect(self.connect)
        self.button_save.clicked.connect(self.save_chart_data)
        self.button_clear.clicked.connect(self.clear_chart)



    def MyUi(self):
        '''
        Method to create the main GUI elements including the matplotlib graph
        and input settings.
        '''

        # The main layout is a QHbox
        hbox = qt.QHBoxLayout()
        hbox.addStretch(1)

        # Buttons
        buttons = qt.QVBoxLayout()
        self.input_mqttserver = qt.QLineEdit()
        self.input_mqttserver.setPlaceholderText("Server Address")
        self.input_mqttserver.setText("localhost")

        self.input_mqttport = qt.QLineEdit()
        self.input_mqttport.setPlaceholderText("Server Port")
        self.input_mqttport.setText("1883")

        self.input_mqtttopic = qt.QLineEdit()
        self.input_mqtttopic.setPlaceholderText("Topic")
        self.input_mqtttopic.setText("testing")

        self.button_connect = qt.QPushButton("Connect")

        self.button_save = qt.QPushButton("Save Chart Data")
        self.button_clear = qt.QPushButton("Clear Chart")

        buttons.addWidget(self.input_mqttserver)
        buttons.addWidget(self.input_mqttport)
        buttons.addWidget(self.input_mqtttopic)
        buttons.addWidget(self.button_connect)
        buttons.addWidget(self.button_save)
        buttons.addWidget(self.button_clear)
        buttons.addStretch(1)

        # Make an initially blank matplotlib canvas and axis
        chart_vbox = qt.QVBoxLayout()
        self.fig = Figure()
        self.static_canvas = FigureCanvas(self.fig)
        self.toolbar = NavigationToolbar(self.static_canvas, self)
        self.ax = self.fig.add_subplot(111)
        # self.ax.plot(3, 'o')
        self.ax.grid()
        self.static_canvas.draw()

        # Add the widgets to chart layout
        chart_vbox.addWidget(self.static_canvas)
        chart_vbox.addWidget(self.toolbar)

        # Add the layouts to the main layout
        hbox.addLayout(chart_vbox)
        hbox.addLayout(buttons)

        self.setLayout(hbox)
        self.setGeometry(300, 300, 600, 350)
        self.setWindowTitle("MQTT Plotter")
        self.show()

    def connect(self):
        '''
        Connections to the
        '''
        self.client.connect(self.input_mqttserver.text(),
                            int(self.input_mqttport.text()), 60)
        self.client.loop_start()


    def disconnect(self):
        self.client.loop_stop()
        self.client.unsubscribe(self.input_mqtttopic.text())
        self.client.disconnect()

    def update_plot(self, data):
        '''
        Updates the chart with a new data point (or array of points) which are
        specified in the "data" parameter.
        '''
        # print("Got something")
        # print(data)
        self.data = np.append(self.data, data)

        # Save a binary backup of the data array
        np.save('data_backup', self.data)

        # Clear the axis, re-draw the grid, plot the data and draw the canvas
        self.ax.clear()
        self.ax.grid()
        self.ax.plot(self.data)
        self.static_canvas.draw()

    def save_chart_data(self):
        '''
        Shows a file selection dialog to specify a filename and then saves the
        data array to that file.
        '''
        fname = ""
        fname = qt.QFileDialog.getSaveFileName(self, 'Select file')
        #print(fname)
        if len(fname[0]) > 0:
            np.savetxt(fname[0], self.data)
            print("Saved to {}".format(fname[0]))

    def clear_chart(self):
        '''
        Shows a confirmation dialog box and then clears the chart and
        data array.
        '''
        msg = qt.QMessageBox()
        msg.setIcon(qt.QMessageBox.Information)
        msg.setText("Chart data will be irretrievably cleared.")
        msg.setInformativeText("Are you sure you want to clear it?")
        msg.setWindowTitle("Confirm Clear")
        msg.setStandardButtons(qt.QMessageBox.Ok | qt.QMessageBox.Cancel)

        retval = msg.exec_()
        if retval == 1024:
            self.data = np.array([])
            self.ax.clear()
            self.ax.grid()
            self.static_canvas.draw()

if __name__ == '__main__':

    data_queue = multiprocessing.Queue()


    app = qt.QApplication(sys.argv)
    window = gui(data_queue)
    window.show()
    app.exec()

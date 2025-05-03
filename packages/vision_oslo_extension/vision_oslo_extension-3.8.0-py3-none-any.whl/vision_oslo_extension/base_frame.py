#
# -*- coding: utf-8  -*-
#=================================================================
# Created by: Jieming Ye
# Created on: Feb 2024
# Last Update: Feb 2024
#=================================================================
# Copyright (c) 2024 [Jieming Ye]
#
# This Python source code is licensed under the 
# Open Source Non-Commercial License (OSNCL) v1.0
# See LICENSE for details.
#=================================================================
"""
Pre-requisite: 
N/A 
Used Input:
N/A
Expected Output:
N/A
Description:
This script defines the base frame to be used all other pages except the first page which is defined in gui_start.py. 
This defines frame creation method, common button action and comment input action.

"""
#=================================================================
# VERSION CONTROL
# V1.0 (Jieming Ye) - Initial Version
#=================================================================
# Set Information Variable
# N/A
#=================================================================

import tkinter as tk
from tkinter import filedialog
from vision_oslo_extension.shared_contents import SharedMethods,SharedVariables # relative import

import os

class BasePage(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller

    def create_frame(self, fill=None, side = None, row_weights=None, column_weights=None):
        frame = tk.Frame(self)
        if fill:
            frame.pack(fill=fill,side=side)
        if row_weights:
            for i, weight in enumerate(row_weights):
                frame.rowconfigure(i, weight=weight)
        if column_weights:
            for i, weight in enumerate(column_weights):
                frame.columnconfigure(i, weight=weight)
        return frame
    
    def get_entry_value(self):
        user_input = SharedVariables.sim_variable.get()
        print("User Input: ", user_input )
        #return user_input

    def button_callback(self,target_page):
        self.get_entry_value()
        self.controller.show_frame(target_page)

    def auto_excel_select(self, input):
        initial_dir = os.getcwd()
        file_path = filedialog.askopenfilename(title="Select File...", initialdir=initial_dir)
        if file_path:
            print(f"Selected file: {file_path}")
            file_name = os.path.basename(file_path)
            # Split the file name based on the last dot
            simname = '.'.join(file_name.split('.')[:-1]) if '.' in file_name else file_name
            #print(simname)
            input.set(simname)
            # update the working directory to the selected file's directory
            selected_dir = os.path.dirname(file_path)
            selected_dir = os.path.normpath(selected_dir)  # normalize the path (use "\\"" instead of windows stype "/"")
            if selected_dir != os.getcwd():
                os.chdir(selected_dir)
                self.controller.working_directory.set(selected_dir)
                SharedMethods.print_message(f"WARNING: Working directiory set to:\n{selected_dir}","33")

    
    def auto_file_select(self, input):
        initial_dir = os.getcwd()
        file_path = filedialog.askopenfilename(title="Select File...", initialdir=initial_dir)
        if file_path:
            print(f"Selected file: {file_path}")
            file_name = os.path.basename(file_path)
            input.set(file_name)
            # update the working directory to the selected file's directory
            selected_dir = os.path.dirname(file_path)
            selected_dir = os.path.normpath(selected_dir)  # normalize the path (use "\\"" instead of windows stype "/"")
            if selected_dir != os.getcwd():
                os.chdir(selected_dir)
                self.controller.working_directory.set(selected_dir)
                SharedMethods.print_message(f"WARNING: Working directiory set to:\n{selected_dir}","33")

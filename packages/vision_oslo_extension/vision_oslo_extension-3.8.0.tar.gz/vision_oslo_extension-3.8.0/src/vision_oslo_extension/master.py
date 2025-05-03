#
# -*- coding: utf-8  -*-
#=================================================================
# Created by: Jieming Ye
# Created on: Nov 2023
# Last Modified: Feb 2024
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
Start GUI
Description:
This module is the package entry.
This module is the only module to be called from User End script directly.

"""
#=================================================================
# VERSION CONTROL
# V1.0 (Jieming Ye) - Initial Version
# V2.0 (Jieming Ye) - Including License Check
#=================================================================
# Set Information Variable
# N/A
#=================================================================

print('Loading....')

from vision_oslo_extension import licensing
from vision_oslo_extension import gui_start

# Main function to start the application
def main():
    # Check the registry for license status
    if not licensing.main():
        input("Press any key to exit.....")  # Keeps the console open until the user presses Enter
        return

    # Initialize and start the GUI application
    app = gui_start.SampleApp()
    app.mainloop()

# programme running
if __name__ == '__main__':
    main()    
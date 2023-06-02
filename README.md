# ROS2 Ender3 syringe pumps

This repository contains code for controlling syringe pumps using image-based feedback. The code is separated into three ROS2 packages, Control, Gui and Vision.
This code was written as part of a Thesis project. Some parts of the code might be unfinished, bugged or working incorrectly. 


## Packages
control: This package provides ROS2 nodes and utilities for controlling the pumps. It includes a teleop node for teleoperating the Ender3 using a keyboard, and several nodes (with or without feedback control) for sending commands to the Ender3 motion controller.

vision: This package provides ROS2 nodes and utilities for processing images from a camera. It includes a camera node for capturing images from a camera (dinolite) and publishing them on a ROS2 topic, and detection nodes for detecting objects in the images using computer vision algorithms based on OpenCV.

gui: This package provides a graphical user interface for controlling the system and viewing the images. It includes a range filter to set (and see) image detection thresholds, as well as a simplified user interface for writing GCode and sending it to the printer.


## Installation
To use these packages, you will need to have ROS2 Humble installed on your system. You can install ROS2 by following the instructions on the ROS2 website: 
https://docs.ros.org/en/humble/index.html

Once you have ROS2 installed, you can clone this repository and build the packages using the following commands:

cd ~/ros2_ws/src

git clone https://github.com/bramros2/ROS_Ender3.git

cd ..

colcon build

## Usage
To use the packages, you will need to run the following nodes:

'teleop_pumps': To teleoperate the Ender3 using the keyboard, run the following command:
ros2 run control teleoppump

'keypress_control': Recieves the commands from the teleoppump node and sends GCode to the Ender3 based on the input. You can manually edit/add more commands to the script. To run, use:
ros2 run control keycontrol

'PID_controller': Feedback controller that takes the current feedrate and adjusts the speed of the pumps based on the difference between the measured size and wanted size of droplets. To use:
ros2 run control pid

çontrol_node': Node that initializes and sends commands to Ender3 based on PID feedback recieved from PID_controller

'flow_node': Unfinished node that should be rewritten to detect channel width. Currently not used
ros2 run vision flow_find

'dinolite': Camere capture node*. 
ros2 run vision dino

*Mostly used for secondary (USB) cameras. For Normal PiCamera, code from https://gitlab.com/boldhearts/ros2_v4l2_camera/-/tree/rolling/ was used.

'droplet_node': Image detection using opencv. Detects droplets based on image thresholding and settings. Publishes average droplet size. To use:
ros2 run vision drop_find

'size_plot': Node that plots droplet sizes measured by image detection. To use:
ros2 run vision plot



## License
This software is released under the MIT License

## Contact
If you have any questions or issues with the packages, please contact the author at bramo@live.nl.

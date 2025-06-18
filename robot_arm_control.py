import json
import sys
import math
import numpy as np
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                           QHBoxLayout, QSlider, QLabel, QGridLayout, QGraphicsView, QGraphicsScene, QGraphicsItem, QPushButton, QCheckBox, QColorDialog)
from PyQt5.QtCore import Qt, QPoint, QRectF
from PyQt5.QtGui import QPainter, QPen, QColor, QMouseEvent
from robot_arm_graphics import RobotArmGraphicsItem
from serial_communication import SerialCommunication  # Import the SerialCommunication class

class RobotArmControl(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Robot Arm Control")
        self.setMinimumSize(1200, 600)

        # Load configuration
        self.load_config()

        # Initialize serial communication
        self.serial_comm = SerialCommunication(port=self.config['serial']['port'], baudrate=self.config['serial']['baudrate'])
        self.serial_comm.connect()

        # Create main widget and layout
        main_widget = QWidget()
        self.setCentralWidget(main_widget)

        # Create a QGraphicsView to allow overlapping
        self.graphics_view = QGraphicsView(self)
        self.graphics_view.setScene(QGraphicsScene(self))
        self.graphics_view.setRenderHint(QPainter.Antialiasing)

        # Create first robot arm visualization
        self.robot_arm1 = RobotArmGraphicsItem(1, self)
        self.graphics_view.scene().addItem(self.robot_arm1)

        # Create second robot arm visualization
        self.robot_arm2 = RobotArmGraphicsItem(2, self)
        self.graphics_view.scene().addItem(self.robot_arm2)

        # Set initial angles from config for each arm independently
        self.robot_arm1.joint_angles = self.config['robot_arm']['initial_angles'][:]
        self.robot_arm2.joint_angles = self.config['robot_arm']['initial_angles'][:]

        # Set the layout for the main widget
        layout = QVBoxLayout(main_widget)
        layout.addWidget(self.graphics_view)

        # Create control panel for both arms
        control_panel = QWidget()
        control_layout = QVBoxLayout(control_panel)

        # Create separate lists for labels, sliders, color buttons, and color previews for both arms
        self.labels1 = []
        self.labels2 = []
        self.sliders1 = []
        self.sliders2 = []
        self.color_buttons1 = []
        self.color_buttons2 = []
        self.color_previews1 = []
        self.color_previews2 = []

        for i in range(5):
            # Create horizontal layout for each joint
            joint_layout = QHBoxLayout()

            # Create label for the first arm
            label1 = QLabel(f"Arm 1 - Joint {i+1}: {self.robot_arm1.joint_angles[i]}°")
            self.labels1.append(label1)
            joint_layout.addWidget(label1)

            # Create horizontal slider for the first arm
            slider1 = QSlider(Qt.Horizontal)
            slider1.setMinimum(-90)
            slider1.setMaximum(90)
            slider1.setValue(self.robot_arm1.joint_angles[i])
            slider1.valueChanged.connect(lambda value, index=i: self.update_joint1(index, value))
            self.sliders1.append(slider1)
            joint_layout.addWidget(slider1)

            # Create color button for the first arm
            color_button1 = QPushButton("Select Color")
            color_button1.clicked.connect(lambda _, index=i: self.select_color(index, arm=1))
            self.color_buttons1.append(color_button1)
            joint_layout.addWidget(color_button1)

            # Create color preview for the first arm
            color_preview1 = QLabel()
            color_preview1.setFixedSize(30, 30)
            color_preview1.setStyleSheet("background-color: black;")  # Default color
            self.color_previews1.append(color_preview1)
            joint_layout.addWidget(color_preview1)

            # Create label for the second arm
            label2 = QLabel(f"Arm 2 - Joint {i+1}: {self.robot_arm2.joint_angles[i]}°")
            self.labels2.append(label2)
            joint_layout.addWidget(label2)

            # Create horizontal slider for the second arm
            slider2 = QSlider(Qt.Horizontal)
            slider2.setMinimum(-90)
            slider2.setMaximum(90)
            slider2.setValue(self.robot_arm2.joint_angles[i])
            slider2.valueChanged.connect(lambda value, index=i: self.update_joint2(index, value))
            self.sliders2.append(slider2)
            joint_layout.addWidget(slider2)

            # Create color button for the second arm
            color_button2 = QPushButton("Select Color")
            color_button2.clicked.connect(lambda _, index=i: self.select_color(index, arm=2))
            self.color_buttons2.append(color_button2)
            joint_layout.addWidget(color_button2)

            # Create color preview for the second arm
            color_preview2 = QLabel()
            color_preview2.setFixedSize(30, 30)
            color_preview2.setStyleSheet("background-color: black;")  # Default color
            self.color_previews2.append(color_preview2)
            joint_layout.addWidget(color_preview2)

            control_layout.addLayout(joint_layout)

        # Add a checkbox for synchronization
        self.sync_checkbox = QCheckBox("Sync Arms")
        self.sync_checkbox.stateChanged.connect(self.sync_arms)
        control_layout.addWidget(self.sync_checkbox)

        # Add a checkbox for duplicating colors
        self.duplicate_color_checkbox = QCheckBox("Duplicate Colors")
        control_layout.addWidget(self.duplicate_color_checkbox)

        # Add buttons for full arm color selection
        full_color_button1 = QPushButton("Select Full Arm Color for Arm 1")
        full_color_button1.clicked.connect(lambda: self.select_full_arm_color(1))
        control_layout.addWidget(full_color_button1)

        full_color_button2 = QPushButton("Select Full Arm Color for Arm 2")
        full_color_button2.clicked.connect(lambda: self.select_full_arm_color(2))
        control_layout.addWidget(full_color_button2)

        layout.addWidget(control_panel)

    def load_config(self):
        with open('config.json', 'r') as config_file:
            self.config = json.load(config_file)

    def sync_arms(self):
        if self.sync_checkbox.isChecked():
            # Sync the angles of the second arm to the first arm
            for i in range(5):
                self.robot_arm2.joint_angles[i] = -self.robot_arm1.joint_angles[i]
                self.sliders2[i].setValue(int(self.robot_arm2.joint_angles[i]))  # Update the slider for arm 2
            self.robot_arm2.update()  # Update the visualization for arm 2

    def update_joint1(self, joint_index, value):
        # Update the joint angle for the first arm
        self.robot_arm1.joint_angles[joint_index] = int(round(value))  # Round and convert to integer
        
        # Update the visualization
        self.robot_arm1.update()
        
        # If sync is enabled, update the second arm
        if self.sync_checkbox.isChecked():
            self.robot_arm2.joint_angles[joint_index] = -self.robot_arm1.joint_angles[joint_index]  # Flip the angle for the second arm
            self.sliders2[joint_index].setValue(self.robot_arm2.joint_angles[joint_index])  # Update the slider for arm 2
            self.robot_arm2.update()  # Update the visualization for arm 2

        # Print the current state of Arm 1
        self.print_arm_state(1)

    def update_joint2(self, joint_index, value):
        # Update the joint angle for the second arm
        self.robot_arm2.joint_angles[joint_index] = int(round(value))  # Round and convert to integer
        
        # Update the visualization
        self.robot_arm2.update()
        
        # If sync is enabled, update the first arm
        if self.sync_checkbox.isChecked():
            self.robot_arm1.joint_angles[joint_index] = -self.robot_arm2.joint_angles[joint_index]  # Flip the angle for the first arm
            self.sliders1[joint_index].setValue(self.robot_arm1.joint_angles[joint_index])  # Update the slider for arm 1
            self.robot_arm1.update()  # Update the visualization for arm 1

        # Print the current state of Arm 2
        self.print_arm_state(2)

    def print_arm_state(self, arm_number):
        if arm_number == 1:
            angles = self.robot_arm1.joint_angles
            colors = [color.name() for color in self.robot_arm1.segment_colors]
        else:
            angles = self.robot_arm2.joint_angles
            colors = [color.name() for color in self.robot_arm2.segment_colors]

        # Convert angles to the new format
        converted_angles = [angle + 90 for angle in angles]  # Convert -90 to 0, 90 to 180

        output = f"${arm_number}:"
        for i in range(5):
            output += f"{int(converted_angles[i])}:{colors[i]}"  # Ensure angles are integers
            if i < 4:  # Add a separator for all but the last joint
                output += ":"

        print(output)  # Print the formatted output to the terminal

    def update_sliders(self):
        for i in range(5):
            self.sliders1[i].setValue(int(self.robot_arm1.joint_angles[i]))  # Update first arm slider
            self.sliders2[i].setValue(int(self.robot_arm2.joint_angles[i]))  # Update second arm slider

    def select_color(self, joint_index, arm):
        color = QColorDialog.getColor()  # Open color dialog
        if color.isValid():
            if arm == 1:
                self.robot_arm1.segment_colors[joint_index] = color  # Set color for arm 1
                self.color_previews1[joint_index].setStyleSheet(f"background-color: {color.name()};")  # Update preview
                if self.duplicate_color_checkbox.isChecked():
                    self.robot_arm2.segment_colors[joint_index] = color  # Duplicate color to arm 2
                    self.color_previews2[joint_index].setStyleSheet(f"background-color: {color.name()};")  # Update preview for arm 2
                    # Print the current state of Arm 2 after color duplication
                    self.print_arm_state(2)
            else:
                self.robot_arm2.segment_colors[joint_index] = color  # Set color for arm 2
                self.color_previews2[joint_index].setStyleSheet(f"background-color: {color.name()};")  # Update preview
                if self.duplicate_color_checkbox.isChecked():
                    self.robot_arm1.segment_colors[joint_index] = color  # Duplicate color to arm 1
                    self.color_previews1[joint_index].setStyleSheet(f"background-color: {color.name()};")  # Update preview for arm 1
                    # Print the current state of Arm 1 after color duplication
                    self.print_arm_state(1)
            
            self.robot_arm1.update()  # Update visualization for arm 1
            self.robot_arm2.update()  # Update visualization for arm 2

            # Print the current state of the arm after color change
            self.print_arm_state(arm)

    def select_full_arm_color(self, arm):
        color = QColorDialog.getColor()  # Open color dialog
        if color.isValid():
            if arm == 1:
                for i in range(5):
                    self.robot_arm1.segment_colors[i] = color  # Set color for all segments of arm 1
                    self.color_previews1[i].setStyleSheet(f"background-color: {color.name()};")  # Update preview
                self.robot_arm1.update()  # Update visualization for arm 1
                # Print the current state of Arm 1 after color change
                self.print_arm_state(1)
            else:
                for i in range(5):
                    self.robot_arm2.segment_colors[i] = color  # Set color for all segments of arm 2
                    self.color_previews2[i].setStyleSheet(f"background-color: {color.name()};")  # Update preview
                self.robot_arm2.update()  # Update visualization for arm 2
                # Print the current state of Arm 2 after color change
                self.print_arm_state(2)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = RobotArmControl()
    window.show()
    sys.exit(app.exec_()) 
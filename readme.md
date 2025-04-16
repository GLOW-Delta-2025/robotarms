# Robot Arm Control Application

This project is a Python application for controlling a robot arm with a graphical user interface (GUI). The application allows users to manipulate the angles of the robot arm's joints and visualize the movements in real-time. It also supports color customization for each joint and the entire arm.

## Features

- Control two robot arms independently.
- Real-time visualization of joint movements.
- Adjustable joint angles with sliders.
- Color customization for each joint and the entire arm.
- Synchronization option to move both arms simultaneously.
- Serial communication to send joint angles and colors.

## Requirements

- Python 3.x
- PyQt5
- PySerial

You can install the required packages using the following command:

```bash
pip install -r requirements.txt
```

## Configuration

The application uses a configuration file named `config.json` to set up initial parameters such as the serial port and baud rate. Below is an example of the configuration file:

```json
{
    "serial": {
        "port": "COM3",
        "baudrate": 9600
    },
    "robot_arm": {
        "link_lengths": [80, 80, 80, 8s0, 80],
        "initial_angles": [0, 0, 0, 0, 0]
    }
}
```

## Usage

**Run the Application**: Execute the following command to start the application:

   ```bash
   python main.py
   ```
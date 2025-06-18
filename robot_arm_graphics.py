import math
from PyQt5.QtWidgets import QGraphicsItem
from PyQt5.QtCore import QPoint, QRectF
from PyQt5.QtGui import QPainter, QPen, QColor, QMouseEvent
from PyQt5.QtCore import Qt  # Add this import for the Qt namespace

class RobotArmGraphicsItem(QGraphicsItem):
    def __init__(self, arm_id, parent_control=None):
        super().__init__(None)
        self.arm_id = arm_id
        self.joint_angles = [0, 0, 0, 0, 0]
        self.link_lengths = [80, 80, 80, 80, 80]
        self.selected_joint = None
        self.joint_positions = []
        self.dragging = False
        self.parent_control = parent_control
        self.segment_colors = [QColor(0, 0, 0) for _ in range(5)]

    def calculate_joint_positions(self):
        self.joint_positions = []
        start_x = 400 + (self.arm_id - 1) * 100
        start_y = 500
        current_x = start_x
        current_y = start_y
        current_angle = -math.pi / 2

        self.joint_positions.append(QPoint(start_x, start_y))

        for i in range(5):
            current_angle += math.radians(self.joint_angles[i])
            end_x = current_x + self.link_lengths[i] * math.cos(current_angle)
            end_y = current_y + self.link_lengths[i] * math.sin(current_angle)
            self.joint_positions.append(QPoint(int(end_x), int(end_y)))
            current_x = end_x
            current_y = end_y

    def get_joint_at_position(self, pos):
        for i, joint_pos in enumerate(self.joint_positions):
            distance = math.sqrt((pos.x() - joint_pos.x())**2 + (pos.y() - joint_pos.y())**2)
            if distance < 10:  # 10 pixels radius for joint selection
                return i
        return None

    def calculate_angle(self, joint_index, mouse_pos):
        if joint_index == 0:
            # For base joint, calculate angle relative to vertical
            base_pos = self.joint_positions[0]
            dx = mouse_pos.x() - base_pos.x()
            dy = mouse_pos.y() - base_pos.y()
            angle = math.degrees(math.atan2(dy, dx))
            # Adjust for upward pointing
            angle += 90
            return angle
        else:
            # For other joints, calculate relative to previous segment
            prev_pos = self.joint_positions[joint_index - 1]
            current_pos = self.joint_positions[joint_index]
            dx = mouse_pos.x() - prev_pos.x()
            dy = mouse_pos.y() - prev_pos.y()
            angle = math.degrees(math.atan2(dy, dx))

            # Calculate previous segment angle
            prev_dx = current_pos.x() - prev_pos.x()
            prev_dy = current_pos.y() - prev_pos.y()
            prev_angle = math.degrees(math.atan2(prev_dy, prev_dx))

            # Calculate relative angle
            relative_angle = angle - prev_angle

            # Normalize to -180 to 180 range
            while relative_angle > 180:
                relative_angle -= 360
            while relative_angle < -180:
                relative_angle += 360

            return relative_angle

    def paint(self, painter, option, widget=None):
        painter.setRenderHint(QPainter.Antialiasing)
        pen = QPen(Qt.black, 2)  # Now Qt is defined
        painter.setPen(pen)

        # Start position (center of the widget)
        start_x = 400 + (self.arm_id - 1) * 100  # Adjust starting position based on arm ID
        start_y = 500  # Adjusted base position to start lower

        # Draw the robot arm
        current_x = start_x
        current_y = start_y
        current_angle = -math.pi / 2  # Start pointing upward (-90 degrees)

        # Calculate and store joint positions
        self.joint_positions = [QPoint(start_x, start_y)]

        for i in range(5):
            # Add the current joint angle to the cumulative angle
            current_angle += math.radians(self.joint_angles[i])

            # Calculate end point of current segment
            end_x = current_x + self.link_lengths[i] * math.cos(current_angle)
            end_y = current_y + self.link_lengths[i] * math.sin(current_angle)

            # Set the color for the current segment
            painter.setPen(QPen(self.segment_colors[i], 2))  # Use the segment color
            painter.drawLine(int(current_x), int(current_y), int(end_x), int(end_y))

            # Draw joint point
            if i == self.selected_joint:
                painter.setBrush(Qt.green)  # Highlight selected joint
            else:
                painter.setBrush(Qt.red)
            painter.drawEllipse(int(current_x - 5), int(current_y - 5), 10, 10)

            # Store joint position
            self.joint_positions.append(QPoint(int(end_x), int(end_y)))

            # Update current position for next segment
            current_x = end_x
            current_y = end_y

        # Draw the end effector
        painter.setBrush(Qt.blue)
        painter.drawEllipse(int(current_x - 5), int(current_y - 5), 10, 10)

    def boundingRect(self):
        return QRectF(0, 0, 800, 600)  # Adjust as needed

    def mousePressEvent(self, event: QMouseEvent):
        if event.button() == Qt.LeftButton:
            self.calculate_joint_positions()
            self.selected_joint = self.get_joint_at_position(event.pos())
            if self.selected_joint is not None:
                self.dragging = True

    def mouseMoveEvent(self, event: QMouseEvent):
        if self.dragging and self.selected_joint is not None:
            new_angle = self.calculate_angle(self.selected_joint, event.pos())

            # Limit the angle to ±90 degrees
            if new_angle > 90:
                new_angle = 90
            elif new_angle < -90:
                new_angle = -90

            self.joint_angles[self.selected_joint] = new_angle
            self.update()
            # Update sliders when the arm is changed
            self.parent_control.update_sliders()  # Call the update_sliders method in RobotArmControl

    def mouseReleaseEvent(self, event: QMouseEvent):
        if event.button() == Qt.LeftButton:
            self.dragging = False
            self.selected_joint = None

    # Other methods remain unchanged...

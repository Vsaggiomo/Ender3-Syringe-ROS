import sys
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QWidget, QLabel, QLineEdit, QPushButton, QVBoxLayout, QApplication, QHBoxLayout, \
    QMessageBox, QTextEdit, QScrollArea
import rclpy
import serial 
import serial.tools.list_ports

from rclpy.node             import Node
from std_msgs.msg           import String


class PubNode(Node):
    def __init__(self):
        super().__init__('pubnode')
        self.publisher = self.create_publisher(String, 'command_input',10)

    def send_input(self, input_string):
        msg = String()
        msg.data = input_string
        self.publisher.publish(msg)


class KeyControlWidget(QWidget):
    def __init__(self):
        super().__init__()
        rclpy.init()
        self.pubnode = PubNode()

        # Set window size
        self.setGeometry(0, 0, 1360, 800)

        # Create labels and line edits for input
        self.x_label = QLabel('X')
        self.x_label.setFixedWidth(100)
        self.x_input = QLineEdit()
        self.x_input.setFixedWidth(100)
        self.x_label.setAlignment(Qt.AlignLeft)
        self.x_input.setAlignment(Qt.AlignLeft)

        self.y_label = QLabel('Y')
        self.y_input = QLineEdit()
        self.y_input.setFixedWidth(100)

        self.z_label = QLabel('Z')
        self.z_input = QLineEdit()
        self.z_input.setFixedWidth(100)

        self.feedrate_label = QLabel('Feedrate')
        self.feedrate_input = QLineEdit()
        self.feedrate_input.setFixedWidth(100)

        # Create button to format input
        self.format_button = QPushButton('Format Input')
        self.format_button.setFixedWidth(100)
        self.format_button.clicked.connect(self.format_input)

        # Create button to clear input
        self.clear_button = QPushButton('Clear Input')
        self.clear_button.setFixedWidth(100)
        self.clear_button.clicked.connect(self.clear_input)

        # Create button to send Gcode to serial
        self.send_button = QPushButton('Send Input to Pumps')
        self.send_button.setFixedWidth(200)
        self.send_button.clicked.connect(self.send_input)

        # Create text edit for displaying formatted text
        self.display_text_edit = QTextEdit()
        self.display_text_edit.setReadOnly(True)
        self.formatted_text = ''

        # Create scroll area widget
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)

        # Set up layout
        mainlay = QHBoxLayout()
        rlay = QVBoxLayout()
        layout = QVBoxLayout()
        xlay = QHBoxLayout()

        # Set up scrollable display text
        scroll_widget = QWidget()
        scroll_widget.setLayout(QVBoxLayout())
        scroll_widget.layout().addWidget(self.display_text_edit)
        scroll_area.setWidget(scroll_widget)
        rlay.addWidget(scroll_area)
        rlay.addWidget(self.send_button, alignment=Qt.AlignRight)

        # Set up layout for x input
        xlay.addWidget(self.x_label, alignment=Qt.AlignLeft)
        xlay.addWidget(self.x_input, alignment=Qt.AlignLeft)
        layout.addLayout(xlay)

        # Set up layout for y input
        ylay = QHBoxLayout()
        ylay.addWidget(self.y_label, alignment=Qt.AlignLeft)
        ylay.addWidget(self.y_input, alignment=Qt.AlignLeft)
        layout.addLayout(ylay)

        # Set up layout for z input
        zlay = QHBoxLayout()
        zlay.addWidget(self.z_label, alignment=Qt.AlignLeft)
        zlay.addWidget(self.z_input, alignment=Qt.AlignLeft)
        layout.addLayout(zlay)

        # Set up layout for feedrate input
        flay = QHBoxLayout()
        flay.addWidget(self.feedrate_label, alignment=Qt.AlignLeft)
        flay.addWidget(self.feedrate_input, alignment=Qt.AlignLeft)
        layout.addLayout(flay)

        # Set up layout for format and clear buttons
        button_layout = QHBoxLayout()
        button_layout.addWidget(self.format_button, alignment=Qt.AlignLeft)
        button_layout.addWidget(self.clear_button, alignment=Qt.AlignLeft)
        layout.addLayout(button_layout)

        # Add all layouts to main layout
        mainlay.addLayout(layout)
        mainlay.addLayout(rlay)
        self.setLayout(mainlay)

    def format_input(self):
        # Get input values, defaulting to 0 if no value entered for x, y, or z
        x = float(self.x_input.text() or 0)
        y = float(self.y_input.text() or 0)
        z = float(self.z_input.text() or 0)

        # Check if feedrate value is entered
        if not self.feedrate_input.text():
            # Display error message if no feedrate value entered
            error_msg = QMessageBox()
            error_msg.setIcon(QMessageBox.Warning)
            error_msg.setText('Please enter a value for feedrate')
            error_msg.setWindowTitle('Error')
            error_msg.exec_()
            return

        # Get feedrate value
        feedrate = float(self.feedrate_input.text())

        # Format input as string
        input_string = 'G1 X{:.2f} Y{:.2f} Z{:.2f} F{:.2f}\n'.format(x, y, z, feedrate)

        # Print formatted input to console
        self.formatted_text += input_string + '\n'
        self.display_text_edit.setText(self.formatted_text)

    def clear_input(self):
        self.x_input.clear()
        self.y_input.clear()
        self.z_input.clear()
        self.feedrate_input.clear()

    def send_input(self):
        # Get formatted input
        input_string = self.formatted_text

        # Check if input is empty
        if not input_string:
            # Display error message if input is empty
            error_msg = QMessageBox()
            error_msg.setIcon(QMessageBox.Warning)
            error_msg.setText('Please format input before sending')
            error_msg.setWindowTitle('Error')
            error_msg.exec_()
            return

        # Create instance of publisher to publish GCode to control node
        self.pubnode.send_input(input_string)

        # Clear input
        self.formatted_text = ''
        self.display_text_edit.clear()
        self.clear_input()

if __name__ == "__main__":
    gui = QApplication(sys.argv)
    g = KeyControlWidget()
    g.show()
    sys.exit(gui.exec_())
import numpy as np
import re
import sys
import cv2
from PyQt5 import QtGui
from PyQt5.QtGui import QImage, QPixmap, QPainter, QPen, QColor
from PyQt5.QtWidgets import QWidget, QApplication, QLabel, QVBoxLayout, QHBoxLayout, QPushButton, QSlider, QMessageBox, \
    QFileDialog, QDialog, QLineEdit
from PyQt5.QtCore import Qt, QTimer, QPointF

class App(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Range Detector")
        self.disply_width = 640
        self.display_height = 480

        self.capture = cv2.VideoCapture(0)
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_frame)
        self.timer.start(5)

        self.video_frame = QLabel(self)
        self.video_frame.resize(self.disply_width, self.display_height)

        self.image_label2 = QLabel(self)
        self.image_label2.resize(self.disply_width,self.display_height)
        # create a text label
        self.textLabel = QLabel('Webcam')
        self.textLabel2 = QLabel('Threshold')

        self.hmin = 0
        self.smin = 0
        self.vmin = 0
        self.hmax = 255
        self.smax = 255
        self.vmax = 255

        hmin_label = QLabel('Minimum Hue:')
        self.hmin_slider = QSlider()
        self.hmin_slider.setMinimum(0)
        self.hmin_slider.setMaximum(255)
        self.hmin_slider.setValue(self.hmin)
        self.hmin_slider.setOrientation(Qt.Horizontal)
        self.hmin_slider.valueChanged.connect(self.on_hmin_slider_changed)
        self.hmin_val_label = QLabel(str(self.hmin))

        smin_label = QLabel('Minimum Saturation:')
        self.smin_slider = QSlider()
        self.smin_slider.setMinimum(0)
        self.smin_slider.setMaximum(255)
        self.smin_slider.setValue(self.smin)
        self.smin_slider.setOrientation(Qt.Horizontal)
        self.smin_slider.valueChanged.connect(self.on_smin_slider_changed)
        self.smin_val_label = QLabel(str(self.smin))

        vmin_label = QLabel('Minimum Value:')
        self.vmin_slider = QSlider()
        self.vmin_slider.setMinimum(0)
        self.vmin_slider.setMaximum(255)
        self.vmin_slider.setValue(self.vmin)
        self.vmin_slider.setOrientation(Qt.Horizontal)
        self.vmin_slider.valueChanged.connect(self.on_vmin_slider_changed)
        self.vmin_val_label = QLabel(str(self.vmin))

        hmax_label = QLabel('Maximum Hue:')
        self.hmax_slider = QSlider()
        self.hmax_slider.setMinimum(0)
        self.hmax_slider.setMaximum(255)
        self.hmax_slider.setValue(self.hmax)
        self.hmax_slider.setOrientation(Qt.Horizontal)
        self.hmax_slider.valueChanged.connect(self.on_hmax_slider_changed)
        self.hmax_val_label = QLabel(str(self.hmax))

        smax_label = QLabel('Maximum Saturation:')
        self.smax_slider = QSlider()
        self.smax_slider.setMinimum(0)
        self.smax_slider.setMaximum(255)
        self.smax_slider.setValue(self.smax)
        self.smax_slider.setOrientation(Qt.Horizontal)
        self.smax_slider.valueChanged.connect(self.on_smax_slider_changed)
        self.smax_val_label = QLabel(str(self.smax))

        vmax_label = QLabel('Maximum Value:')
        self.vmax_slider = QSlider()
        self.vmax_slider.setMinimum(0)
        self.vmax_slider.setMaximum(255)
        self.vmax_slider.setValue(self.vmax)
        self.vmax_slider.setOrientation(Qt.Horizontal)
        self.vmax_slider.valueChanged.connect(self.on_vmax_slider_changed)
        self.vmax_val_label = QLabel(str(self.vmax))

        reset_rect_button = QPushButton('Reset Rectangle')
        reset_rect_button.clicked.connect(self.on_reset_rect_button_clicked)

        reset_button = QPushButton('Reset HSV')
        reset_button.clicked.connect(self.on_reset_button_clicked)

        save_button = QPushButton('Save HSV')
        save_button.clicked.connect(self.on_save_button_clicked)

        load_button = QPushButton('Load HSV')
        load_button.clicked.connect(self.on_load_button_clicked)

        self.draw_line_button = QPushButton('Draw Line')
        self.draw_line_button.setCheckable(True)
        self.draw_line_button.clicked.connect(self.on_draw_line_clicked)

        clear_line_button = QPushButton('Clear Line')
        clear_line_button.clicked.connect(self.on_clear_line_clicked)

        calibrate_button = QPushButton('Calibrate pixel size')
        calibrate_button.clicked.connect(self.on_calibrate_clicked)


        # create a vertical box layout and add the two labels
        top_layout1 = QVBoxLayout()
        top_layout2 = QVBoxLayout()

        top_layout1.addWidget(self.textLabel)
        top_layout1.addWidget(self.video_frame)

        # set the vbox layout as the widgets layout
        top_layout2.addWidget(self.textLabel2)
        top_layout2.addWidget(self.image_label2)

        # set the vbox layout as the widgets layout
        button_layout = QHBoxLayout()
        button_layout.addWidget(reset_rect_button)
        button_layout.addWidget(save_button)
        button_layout.addWidget(load_button)
        button_layout.addWidget(reset_button)

        button0_layout = QHBoxLayout()
        button0_layout.addWidget(self.draw_line_button)
        button0_layout.addWidget(clear_line_button)
        button0_layout.addWidget(calibrate_button)

        bottom_layout = QVBoxLayout()
        hmin_layout = QHBoxLayout()
        hmin_layout.addWidget(hmin_label, alignment=Qt.AlignRight)
        hmin_layout.addWidget(self.hmin_slider, alignment=Qt.AlignRight)
        hmin_layout.addWidget(self.hmin_val_label, alignment=Qt.AlignRight)
        bottom_layout.addLayout(hmin_layout)

        smin_layout = QHBoxLayout()
        smin_layout.addWidget(smin_label, alignment=Qt.AlignRight)
        smin_layout.addWidget(self.smin_slider, alignment=Qt.AlignRight)
        smin_layout.addWidget(self.smin_val_label, alignment=Qt.AlignRight)
        bottom_layout.addLayout(smin_layout)

        vmin_layout = QHBoxLayout()
        vmin_layout.addWidget(vmin_label, alignment=Qt.AlignRight)
        vmin_layout.addWidget(self.vmin_slider, alignment=Qt.AlignRight)
        vmin_layout.addWidget(self.vmin_val_label, alignment=Qt.AlignRight)
        bottom_layout.addLayout(vmin_layout)

        hmax_layout = QHBoxLayout()
        hmax_layout.addWidget(hmax_label, alignment=Qt.AlignRight)
        hmax_layout.addWidget(self.hmax_slider, alignment=Qt.AlignRight)
        hmax_layout.addWidget(self.hmax_val_label, alignment=Qt.AlignRight)
        bottom_layout.addLayout(hmax_layout)

        smax_layout = QHBoxLayout()
        smax_layout.addWidget(smax_label, alignment=Qt.AlignRight)
        smax_layout.addWidget(self.smax_slider, alignment=Qt.AlignRight)
        smax_layout.addWidget(self.smax_val_label, alignment=Qt.AlignRight)
        bottom_layout.addLayout(smax_layout)

        vmax_layout = QHBoxLayout()
        vmax_layout.addWidget(vmax_label, alignment=Qt.AlignRight)
        vmax_layout.addWidget(self.vmax_slider, alignment=Qt.AlignRight)
        vmax_layout.addWidget(self.vmax_val_label, alignment=Qt.AlignRight)
        bottom_layout.addLayout(vmax_layout)

        
        bottom_layout.addLayout(button_layout)

        buttons_layout = QHBoxLayout()
        bottom_layout.addLayout(buttons_layout)
        bottom_layout.addLayout(button0_layout)

        self.rectangle_button = QPushButton("Draw Rectangle", self)
        self.rectangle_button.setCheckable(True)
        self.rectangle_button.clicked.connect(self.draw_rectangle)
        buttons_layout.addWidget(self.rectangle_button)
        
        self.save_rect_button = QPushButton("Save Rect", self)
        self.save_rect_button.clicked.connect(self.save_rect)
        buttons_layout.addWidget(self.save_rect_button)

        self.save_frame_button = QPushButton("Save Frame", self)
        self.save_frame_button.clicked.connect(self.save_frame)
        buttons_layout.addWidget(self.save_frame_button)

        self.subtraction_button = QPushButton("Subtraction", self)
        self.subtraction_button.setCheckable(True)
        self.subtraction_button.clicked.connect(self.toggle_subtraction)
        buttons_layout.addWidget(self.subtraction_button)

        # Create the labels layout and add the labels to it
        labels_layout = QHBoxLayout()
        labels_layout2 = QHBoxLayout()
        bottom_layout.addLayout(labels_layout)
        bottom_layout.addLayout(labels_layout2)

        self.drawing_label = QLabel(self)
        labels_layout.addWidget(self.drawing_label)

        self.start_label = QLabel(self)
        labels_layout2.addWidget(self.start_label)

        self.end_label = QLabel(self)
        labels_layout2.addWidget(self.end_label)

        self.rect_label = QLabel(self)
        labels_layout.addWidget(self.rect_label)

        self.coords_label = QLabel(self)
        labels_layout2.addWidget(self.coords_label)

        self.subtraction_label = QLabel(self)
        labels_layout.addWidget(self.subtraction_label)

        self.stored_label = QLabel(self)
        labels_layout.addWidget(self.stored_label)

        self.background_label = QLabel(self)
        labels_layout2.addWidget(self.background_label)

        # Initialize instance variables
        self.line_drawing = False
        self.is_drawing = False
        self.rect_start = None
        self.rect_start_lbl = None
        self.rect_end = None
        self.rect_end_lbl = None
        self.rectangle = None
        self.line = None
        self.line_start = None
        self.line_end = None
        self.line_start_lbl = None
        self.line_end_lbl = None
        self.stored_frame = None
        self.subtraction_on = False
        self.rectangle_coords = None
        self.background = None
        self.umPerPixel = None

        top_layout = QHBoxLayout()
        top_layout.addLayout(top_layout1)
        top_layout.addLayout(top_layout2)

        layout = QVBoxLayout()
        layout.addLayout(top_layout)
        layout.addLayout(bottom_layout)

        self.setLayout(layout)

    def update_frame(self):
        ret, frame = self.capture.read()
        if ret:
            self.update_mask(frame)
            q_image = QImage(frame.data, frame.shape[1], frame.shape[0], QImage.Format_BGR888)
            painter = QPainter(q_image)
            painter.setPen(QPen(Qt.blue, 2, Qt.SolidLine))
            if self.rect_start is not None:
                painter.setBrush(QColor('red'))
                rect_point = QPointF(*self.rect_start)
                painter.drawEllipse(rect_point, 5, 5)
            if self.rectangle is not None:
                x, y, w, h = self.rectangle
                painter.drawRect(x, y, w, h)
            if self.line is not None:
                x, y, w, h = self.line
                painter.drawRect(x,y,w,h)
            painter.end()
            h, w, ch = frame.shape
            bytes_per_line = ch * w
            self.video_frame.setPixmap(QPixmap.fromImage(q_image).scaled(w, h, Qt.KeepAspectRatio))
            self.update_labels()
                
    def update_mask(self, frame):
        """Updates the image_label2 with a new opencv image"""
        if self.subtraction_on and self.background is not None:
                fgbg = cv2.createBackgroundSubtractorMOG2()
                fgbg.apply(self.background)
                fgmask = fgbg.apply(frame)
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)        
        thresh = cv2.inRange(frame, (self.hmin, self.smin, self.vmin), (self.hmax, self.smax, self.vmax))
        if self.subtraction_on and self.background is not None:
            thresh = cv2.bitwise_and(fgmask,thresh)
            nonimportant, thresh = cv2.threshold(thresh, 0, 255, cv2.THRESH_BINARY)
        qt_img2 = self.convert_cv_qt2(thresh)
        self.image_label2.setPixmap(qt_img2)

    def convert_cv_qt2(self, cv_img):
        """Convert from an opencv image to QPixmap"""
        gray_image = cv_img
        h, w = gray_image.shape
        bytes_per_line = 1 * w
        convert_to_Qt_format = QtGui.QImage(gray_image.data, w, h, bytes_per_line, QtGui.QImage.Format_Grayscale8)
        p = convert_to_Qt_format.scaled(self.disply_width, self.display_height, Qt.KeepAspectRatio)
        return QPixmap.fromImage(p)

    def on_hmin_slider_changed(self, value):
        if self.hmax <= value:
            value = self.hmax -1
        self.hmin = value
        self.hmin_slider.setValue(self.hmin)
        self.hmin_val_label.setText(str(value))

    def on_smin_slider_changed(self, value):
        if self.smax <= value:
            value = self.smax -1
        self.smin = value
        self.smin_slider.setValue(self.smin)
        self.smin_val_label.setText(str(value))

    def on_vmin_slider_changed(self, value):
        if self.vmax <= value:
            value = self.vmax -1
        self.vmin = value
        self.vmin_slider.setValue(self.vmin)
        self.vmin_val_label.setText(str(value))

    def on_hmax_slider_changed(self, value):
        if self.hmin >= value:
            value = self.hmin +1
        self.hmax = value
        self.hmax_slider.setValue(self.hmax)
        self.hmax_val_label.setText(str(value))

    def on_smax_slider_changed(self, value):
        if self.smin >= value:
            value = self.smin +1
        self.smax = value
        self.smax_slider.setValue(self.smax)
        self.smax_val_label.setText(str(value))

    def on_vmax_slider_changed(self, value):
        if self.vmin >= value:
            value = self.vmin +1
        self.vmax = value
        self.vmax_slider.setValue(self.vmax)
        self.vmax_val_label.setText(str(value))

    def on_reset_button_clicked(self):
        self.reset_sliders()

    def on_reset_rect_button_clicked(self):
        self.rectangle = None
        self.update_frame()

    def reset_sliders(self):
        self.hmin = 0
        self.hmin_slider.setValue(self.hmin)
        self.hmin_val_label.setText(str(self.hmin))
        self.smin = 0
        self.smin_slider.setValue(self.smin)
        self.smin_val_label.setText(str(self.smin))
        self.vmin = 0
        self.vmin_slider.setValue(self.vmin)
        self.vmin_val_label.setText(str(self.vmin))
        self.hmax = 255
        self.hmax_slider.setValue(self.hmax)
        self.hmax_val_label.setText(str(self.hmax))
        self.smax = 255
        self.smax_slider.setValue(self.smax)
        self.smax_val_label.setText(str(self.smax))
        self.vmax = 255
        self.vmax_slider.setValue(self.vmax)
        self.vmax_val_label.setText(str(self.vmax))

    def on_save_button_clicked(self):
        file_dialog = QFileDialog(self, 'Save Settings', options=QFileDialog.DontUseNativeDialog)
        file_dialog.setNameFilters(['Text files (*.txt)'])
        file_dialog.setDefaultSuffix('txt')
        
        # get file name to save the settings
        if file_dialog.exec_() == QFileDialog.Accepted:
            file_name = file_dialog.selectedFiles()[0]

            with open(file_name, 'w') as f:
                f.write(f'hmin={self.hmin}\n')
                f.write(f'smin={self.smin}\n')
                f.write(f'vmin={self.vmin}\n')
                f.write(f'hmax={self.hmax}\n')
                f.write(f'smax={self.smax}\n')
                f.write(f'vmax={self.vmax}')
            QMessageBox.information(self, 'Saved', 'Settings saved successfully.')

    def on_load_button_clicked(self):

        file_dialog = QFileDialog(self, 'Open Settings File', options=QFileDialog.DontUseNativeDialog)
        file_dialog.setNameFilters(['Text Files (*.txt)'])

        # Use file dialog to allow user to select a file
        if file_dialog.exec_() == QFileDialog.Accepted:
            file_path = file_dialog.selectedFiles()[0]

            with open(file_path, 'r') as f:
                values = f.read().split('\n')
                if len(values) == 6:
                    try:
                        hmin = int(re.findall("\d+", values[0])[0])
                        smin = int(re.findall("\d+", values[1])[0])
                        vmin = int(re.findall("\d+", values[2])[0])
                        hmax = int(re.findall("\d+", values[3])[0])
                        smax = int(re.findall("\d+", values[4])[0])
                        vmax = int(re.findall("\d+", values[5])[0])

                        # Check that min values are lower than max values
                        if hmin < hmax and smin < smax and vmin < vmax:
                            self.hmin = hmin
                            self.smin = smin
                            self.vmin = vmin
                            self.hmax = hmax
                            self.smax = smax
                            self.vmax = vmax

                            # Update sliders
                            self.hmin_slider.setValue(hmin)
                            self.smin_slider.setValue(smin)
                            self.vmin_slider.setValue(vmin)
                            self.hmax_slider.setValue(hmax)
                            self.smax_slider.setValue(smax)
                            self.vmax_slider.setValue(vmax)

                            # Update labels
                            self.hmin_val_label.setText(str(hmin))
                            self.smin_val_label.setText(str(smin))
                            self.vmin_val_label.setText(str(vmin))
                            self.hmax_val_label.setText(str(hmax))
                            self.smax_val_label.setText(str(smax))
                            self.vmax_val_label.setText(str(vmax))
                        else:
                            QMessageBox.warning(self, "Invalid Values", "The values in the file are not valid.")
                    except ValueError:
                        QMessageBox.warning(self, "Invalid File", "The file does not contain valid integer values.")
                else:
                    QMessageBox.warning(self, "Invalid File", "The file does not contain the correct number of values.")
    def update_labels(self):
            self.drawing_label.setText(f"Drawing: {self.is_drawing}")
            self.start_label.setText(f"Rect start: {self.rect_start_lbl}")
            self.end_label.setText(f"Rect end: {self.rect_end_lbl}")
            self.rect_label.setText(f"Rectangle: {self.rectangle}")
            self.stored_label.setText(f"um/pixel: {self.umPerPixel}")
            self.subtraction_label.setText(f"Subtraction on: {self.subtraction_on}")
            self.coords_label.setText(f"Rect coords: {self.rectangle_coords}")
            self.background_label.setText(f"Background: {self.background is not None}")

    def save_frame(self):
        ret, frame = self.capture.read()
        if ret:
            self.stored_frame = True
            self.background = frame.copy()
    
    def save_rect(self):
        self.rectangle_coords = self.get_rect_coords()

    def get_rect_coords(self):
        if self.rectangle is None:
            return None
        x, y, w, h = self.rectangle
        x_min = round(x / self.capture.get(cv2.CAP_PROP_FRAME_WIDTH), 4)
        x_min = max(0,x_min)
        y_min = round(y / self.capture.get(cv2.CAP_PROP_FRAME_HEIGHT), 4)
        y_min = max(0,y_min)
        x_max = round((x + w) / self.capture.get(cv2.CAP_PROP_FRAME_WIDTH), 4)
        x_max = min(1,x_max)
        y_max = round((y + h) / self.capture.get(cv2.CAP_PROP_FRAME_HEIGHT), 4)
        y_max = min(1,y_max)

        return [x_min, x_max, y_min, y_max]
    
    def toggle_subtraction(self):
        if self.subtraction_on:
            self.subtraction_on = False    
        else:
            self.subtraction_on = True

    def on_draw_line_clicked(self):
        if self.line_drawing:
            self.line_drawing = False
            self.draw_line_button.setChecked(False)
            self.line = self.get_line()             #
            self.line_start_lbl = self.line_start
            self.line_end_lbl = self.line_end
            self.line_start = None
            self.line_end = None
        else:
            self.line_drawing = True
            self.line = None
            self.update_frame()
        if self.line_drawing:
            self.draw_line_button.setStyleSheet('background-color: green; color: white;')
        else:
            self.draw_line_button.setStyleSheet('')

    def get_line(self):
        if self.line_start is None or self.line_end is None:
            return
        x, y, w, h = cv2.boundingRect(np.array([self.line_start, self.line_end]))
        return (x,y,0,h)

    def on_clear_line_clicked(self):
        self.line = None
        self.update_frame()

    def on_calibrate_clicked(self):
        if self.line is None:
            return
        dialog = QDialog(self)
        dialog.setWindowTitle('Calibrate Pixels')
        layout = QVBoxLayout()
        label = QLabel('Enter channel size in um:')
        layout.addWidget(label)
        lineEdit = QLineEdit()
        layout.addWidget(lineEdit)
        button = QPushButton('OK')
        layout.addWidget(button)
        dialog.setLayout(layout)

        def okPressed():
            channelSize = float(lineEdit.text())
            self.umPerPixel = self.calculateUmPerPixel(channelSize)
            dialog.accept()

        button.clicked.connect(okPressed)
        dialog.exec_()

    def calculateUmPerPixel(self, channelSize):
        length = self.line[3]
        umPerPixel = channelSize / length
        return umPerPixel


    def draw_rectangle(self):
        if self.is_drawing:
            self.is_drawing = False
            self.rectangle_button.setChecked(False)
            self.rectangle = self.get_rect()
            self.rect_start_lbl = self.rect_start
            self.rect_end_lbl = self.rect_end
            self.rect_start = None
            self.rect_end = None
        else:
            self.is_drawing = True
            self.rectangle = None
            self.update_frame()
        if self.is_drawing:
            self.rectangle_button.setStyleSheet('background-color: green; color: white;')
        else:
            self.rectangle_button.setStyleSheet('')

    def mousePressEvent(self, event):
        if self.is_drawing:
            if self.rect_start is None:
                # Adjust mouse coordinates to account for videoframe position
                pos = self.video_frame.mapFromGlobal(event.globalPos())
                self.rect_start = (pos.x(), pos.y())
                self.rect_start_lbl = self.rect_start
            else:
                # Adjust mouse coordinates to account for videoframe position
                pos = self.video_frame.mapFromGlobal(event.globalPos())
                self.rect_end = (pos.x(), pos.y())
                self.rect_end_lbl = self.rect_end
                self.draw_rectangle()
        if self.line_drawing:
            if self.line_start is None:
                # Adjust mouse coordinates to account for videoframe position
                pos = self.video_frame.mapFromGlobal(event.globalPos())
                self.line_start = (pos.x(),pos.y())
                self.line_start_lbl = self.line_start[1]
            else:
                # Adjust mouse coordinates to account for videoframe position
                pos = self.video_frame.mapFromGlobal(event.globalPos())
                self.line_end = (pos.x(),pos.y())
                self.line_end_lbl = self.line_end[1]
                self.on_draw_line_clicked()

    def get_rect(self):
        if self.rect_start is None or self.rect_end is None:
            return None
        x, y, w, h = cv2.boundingRect(np.array([self.rect_start, self.rect_end]))
        return (x, y, w, h)

    def closeEvent(self, event):
        self.capture.release()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    a = App()
    a.show()
    sys.exit(app.exec_())

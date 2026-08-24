import random

from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *


class MainWindow(QMainWindow):
    def __init__(self, arduino):
        super().__init__()

        self.arduino = arduino

        self.setGeometry(550, 300, 750, 520)
        self.setWindowTitle("RGB Controller")
        self.setWindowIcon(QIcon("assets/icon.png"))

        self.status_label = QLabel("🔴 Not Connected.")

        self.preview = QFrame()

        self.red_label = QLabel("Red")
        self.green_label = QLabel("Green")
        self.blue_label = QLabel("Blue")

        self.red_dial = QDial()
        self.green_dial = QDial()
        self.blue_dial = QDial()

        dials = [self.red_dial, self.green_dial, self.blue_dial]
        for dial in dials:
            dial.setFixedSize(100, 100)
            dial.setRange(0, 255)
            dial.setValue(0)
            dial.setNotchesVisible(True)
            dial.setNotchTarget(8)
            dial.setSingleStep(5)
            dial.setWrapping(False)

        self.on_btn = QPushButton("ON")
        self.off_btn = QPushButton("OFF")
        self.pick_btn = QPushButton("Pick Color")
        self.random_btn = QPushButton("Random")
        self.dance_btn = QPushButton("Dance!")

        # dance parameters
        self.dancing = False
        self.dance_timer = QTimer()

        self.target_r = 0
        self.target_g = 0
        self.target_b = 0

        # Flag
        self.updating_from_dance = False

        # functions
        self.initUI()
        self.connect_signals()
        self.setup_timer()

    def initUI(self):
        # ---------- Central Widget ----------
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # ---------- Main Layout ----------
        main_layout = QVBoxLayout()
        central_widget.setLayout(main_layout)

        # status label
        self.status_label.setAlignment(Qt.AlignCenter)

        # preview
        self.preview.setFixedSize(320, 180)
        self.preview.setObjectName("preview")

        # ----------
        # RGB panel
        # ----------
        rgb_panel = QFrame()
        rgb_panel.setObjectName("rgbPanel")

        hbox = QHBoxLayout(rgb_panel)

        # red
        red_layout = QVBoxLayout()
        self.red_label.setAlignment(Qt.AlignCenter)
        red_layout.addWidget(self.red_label)
        red_layout.addWidget(self.red_dial)

        # green
        green_layout = QVBoxLayout()
        self.green_label.setAlignment(Qt.AlignCenter)
        green_layout.addWidget(self.green_label)
        green_layout.addWidget(self.green_dial)

        # blue
        blue_layout = QVBoxLayout()
        self.blue_label.setAlignment(Qt.AlignCenter)
        blue_layout.addWidget(self.blue_label)
        blue_layout.addWidget(self.blue_dial)

        hbox.addLayout(red_layout)
        hbox.addLayout(green_layout)
        hbox.addLayout(blue_layout)

        # -------------
        # button panel
        # -------------
        button_panel = QFrame()
        button_panel.setObjectName("buttonPanel")

        button_layout = QHBoxLayout(button_panel)

        button_layout.addWidget(self.on_btn)
        button_layout.addWidget(self.off_btn)
        button_layout.addWidget(self.pick_btn)
        button_layout.addWidget(self.random_btn)
        button_layout.addWidget(self.dance_btn)

        # adding to main layout
        main_layout.addWidget(self.status_label)
        main_layout.addSpacing(15)
        main_layout.addWidget(self.preview, alignment=Qt.AlignHCenter)
        main_layout.addSpacing(20)
        main_layout.addWidget(rgb_panel)
        main_layout.addSpacing(30)
        main_layout.addWidget(button_panel)

    def connect_signals(self):
        self.red_dial.valueChanged.connect(self.dial_changed)
        self.green_dial.valueChanged.connect(self.dial_changed)
        self.blue_dial.valueChanged.connect(self.dial_changed)

        self.on_btn.clicked.connect(self.turn_on)
        self.off_btn.clicked.connect(self.turn_off)
        self.pick_btn.clicked.connect(self.pick_color)
        self.random_btn.clicked.connect(self.random_color)
        self.dance_btn.clicked.connect(self.toggle_dance)

    def update_color(self):
        r = self.red_dial.value()
        g = self.green_dial.value()
        b = self.blue_dial.value()
        self.set_preview_color(r, g, b)

        if self.arduino.ready:
            self.arduino.set_color(r, g, b)

    def set_preview_color(self, r, g, b):
        self.preview.setStyleSheet(f"""
            QFrame {{
                background-color: rgb({r}, {g}, {b});
                border: 2px solid gray;
                border-radius: 8px;
            }}
        """)

    def dial_changed(self):
        if not self.updating_from_dance:
            self.stop_dance()

        self.update_color()

    def turn_on(self):
        self.stop_dance()

        self.red_dial.setValue(255)
        self.green_dial.setValue(255)
        self.blue_dial.setValue(255)
        self.update_color()

    def turn_off(self):
        self.stop_dance()

        self.red_dial.setValue(0)
        self.green_dial.setValue(0)
        self.blue_dial.setValue(0)
        self.update_color()

    def pick_color(self):
        self.stop_dance()

        color_dialog = QColorDialog(self)
        color_dialog.setObjectName("colorPicker")

        if color_dialog.exec():
            color = color_dialog.currentColor()

            self.red_dial.setValue(color.red())
            self.green_dial.setValue(color.green())
            self.blue_dial.setValue(color.blue())

            self.update_color()

    def random_color(self):
        self.stop_dance()

        r = random.randint(0, 255)
        g = random.randint(0, 255)
        b = random.randint(0, 255)

        # update dials
        self.red_dial.setValue(r)
        self.green_dial.setValue(g)
        self.blue_dial.setValue(b)

        # update preview
        self.set_preview_color(r, g, b)

        # send to Arduino
        if self.arduino.ready:
            self.arduino.set_color(r, g, b)

    def toggle_dance(self):
        if not self.dancing:
            self.dancing = True
            self.dance_btn.setText("Stop")

            # pick first target color
            self.target_r = random.randint(0, 255)
            self.target_g = random.randint(0, 255)
            self.target_b = random.randint(0, 255)

            self.dance_timer.start(30)
        else:
            self.dancing = False
            self.dance_btn.setText("Dance!")
            self.dance_timer.stop()

    def dance_step(self):
        # Current values
        r = self.red_dial.value()
        g = self.green_dial.value()
        b = self.blue_dial.value()

        # Smoothly move toward target
        step = 5  # smaller = smoother

        if r < self.target_r: r += step
        if r > self.target_r: r -= step

        if g < self.target_g: g += step
        if g > self.target_g: g -= step

        if b < self.target_b: b += step
        if b > self.target_b: b -= step

        self.updating_from_dance = True
        # update dials
        self.red_dial.setValue(r)
        self.green_dial.setValue(g)
        self.blue_dial.setValue(b)

        self.updating_from_dance = False

        # update preview
        self.set_preview_color(r, g, b)

        # send to Arduino
        if self.arduino.ready:
            self.arduino.set_color(r, g, b)

        # once reached target → pick a new one
        if abs(r - self.target_r) < 5 and abs(g - self.target_g) < 5 and abs(b - self.target_b) < 5:
            self.target_r = random.randint(0, 255)
            self.target_g = random.randint(0, 255)
            self.target_b = random.randint(0, 255)

    def stop_dance(self):
        if self.dancing:
            self.dancing = False
            self.dance_timer.stop()
            self.dance_btn.setText("Dance!")

    # Timer
    def setup_timer(self):
        self.timer = QTimer()
        self.timer.timeout.connect(self.check_arduino)
        self.timer.start(500)

        self.dance_timer.timeout.connect(self.dance_step)
    def check_arduino(self):
        if self.arduino.scan_and_connect():
            self.status_label.setText("🟢 Connected.")
        else:
            self.status_label.setText("🔴 Disconnected.")


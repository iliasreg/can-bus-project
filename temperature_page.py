from PySide6 import QtCore, QtWidgets, QtGui

class TemperaturePage(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        layout = QtWidgets.QHBoxLayout(self)
        self.side = QtWidgets.QGroupBox("Temperature Data")
        self.side.setFixedWidth(280)
        v = QtWidgets.QVBoxLayout(self.side)
        self.temp_label = QtWidgets.QLabel("Temperature: 0.0 °C")
        self.state_label = QtWidgets.QLabel("State: Normal")
        for lbl in [self.temp_label, self.state_label]:
            lbl.setStyleSheet("color:#c8c8c8; font-size:16px;")
            v.addWidget(lbl)
        v.addStretch()
        self.bar = QtWidgets.QProgressBar()
        self.bar.setOrientation(QtCore.Qt.Vertical)
        self.bar.setMinimum(0)
        self.bar.setMaximum(100)
        self.bar.setFixedSize(100, 400)
        layout.addWidget(self.side)
        layout.addWidget(self.bar, alignment=QtCore.Qt.AlignCenter)
        self.temp = 0
        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.update_temp)
        self.timer.start(50)

    def set_temp(self, value):
        self.temp = value

    def update_temp(self):
        val = max(0, min(100, int(self.temp)))
        color = QtGui.QColor.fromHsv(int(240 - (val * 2.4)), 255, 255)
        style = f"""
        QProgressBar::chunk {{
            background-color: {color.name()};
        }}
        QProgressBar {{
            border: 2px solid #333;
            border-radius: 5px;
            background-color: #111;
        }}
        """
        self.bar.setStyleSheet(style)
        self.bar.setValue(val)
        state = "Cold" if val < 15 else "Warm" if val < 35 else "Hot"
        self.temp_label.setText(f"Temperature: {val:.1f} °C")
        self.state_label.setText(f"State: {state}")

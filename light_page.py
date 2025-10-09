from PySide6 import QtCore, QtWidgets, QtGui

class LightPage(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        layout = QtWidgets.QHBoxLayout(self)
        self.side = QtWidgets.QGroupBox("Light Sensor Data")
        self.side.setFixedWidth(280)
        v = QtWidgets.QVBoxLayout(self.side)
        self.lux_label = QtWidgets.QLabel("Lux: 0.0 lx")
        self.state_label = QtWidgets.QLabel("State: Dim")
        for lbl in [self.lux_label, self.state_label]:
            lbl.setStyleSheet("color:#c8c8c8; font-size:16px;")
            v.addWidget(lbl)
        v.addStretch()
        self.label = QtWidgets.QLabel()
        self.label.setFixedSize(400, 400)
        layout.addWidget(self.side)
        layout.addWidget(self.label, alignment=QtCore.Qt.AlignCenter)
        self.lux = 0
        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.update_light)
        self.timer.start(50)

    def set_lux(self, value):
        self.lux = value

    def update_light(self):
        intensity = max(0, min(255, int(self.lux / 4)))
        pixmap = QtGui.QPixmap(400, 400)
        pixmap.fill(QtCore.Qt.transparent)
        painter = QtGui.QPainter(pixmap)
        gradient = QtGui.QRadialGradient(200, 200, 150)
        gradient.setColorAt(0, QtGui.QColor(255, 255, 180, intensity))
        gradient.setColorAt(1, QtGui.QColor(0, 0, 0))
        painter.setBrush(QtGui.QBrush(gradient))
        painter.setPen(QtCore.Qt.NoPen)
        painter.drawEllipse(50, 50, 300, 300)
        painter.end()
        self.label.setPixmap(pixmap)
        state = "Bright" if self.lux > 500 else "Moderate" if self.lux > 100 else "Dim"
        self.lux_label.setText(f"Lux: {self.lux:.1f} lx")
        self.state_label.setText(f"State: {state}")

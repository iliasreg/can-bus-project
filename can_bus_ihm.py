from PySide6 import QtCore, QtWidgets, QtGui
import pyqtgraph as pg
import sys
from collections import deque
from datetime import datetime
from acceleration_page import AccelerationPage
from light_page import LightPage
from temperature_page import TemperaturePage

class ModernCANBusHMI(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("BUS CAN IHM")
        self.resize(1200, 800)

        self.max_data_points = 100
        self.lux_data = deque(maxlen=self.max_data_points)
        self.accel_data = deque(maxlen=self.max_data_points)
        self.temp_data = deque(maxlen=self.max_data_points)
        self.time_data = deque(maxlen=self.max_data_points)

        self.current_values = {'lux': 0.0, 'acceleration': 0.0, 'temperature': 0.0}
        self.is_connected = False
        self.last_update = "Never"
        self.running = True

        self._build_ui()

        self.gui_timer = QtCore.QTimer()
        self.gui_timer.timeout.connect(self._update_gui)
        self.gui_timer.start(50)

    def _build_ui(self):
        self.tabs = QtWidgets.QTabWidget()
        self.tabs.setStyleSheet("""
            QTabWidget::pane { border: 0; background-color: #0f0f0f; }
            QTabBar::tab {
                background-color: #191919;
                color: #c8c8c8;
                padding: 8px 20px;
                border-top-left-radius: 8px;
                border-top-right-radius: 8px;
            }
            QTabBar::tab:selected {
                background-color: #0070f3;
                color: white;
            }
        """)

        self.dashboard_page = QtWidgets.QWidget()
        self._build_dashboard(self.dashboard_page)

        self.accel_page = AccelerationPage()
        self.light_page = LightPage()
        self.temp_page = TemperaturePage()

        self.tabs.addTab(self.dashboard_page, "Dashboard")
        self.tabs.addTab(self.accel_page, "Acceleration")
        self.tabs.addTab(self.light_page, "Light")
        self.tabs.addTab(self.temp_page, "Temperature")

        self.setCentralWidget(self.tabs)

    def _build_dashboard(self, central):
        main_layout = QtWidgets.QVBoxLayout(central)
        main_layout.setContentsMargins(12,12,12,12)
        main_layout.setSpacing(12)

        cards_widget = QtWidgets.QWidget()
        cards_layout = QtWidgets.QHBoxLayout(cards_widget)
        cards_layout.setSpacing(10)

        self.lux_card = self._create_sensor_card("Illuminance", "lux_value", "lux", "rgb(255,193,7)")
        self.accel_card = self._create_sensor_card("Acceleration", "accel_value", "m/s²", "rgb(0,188,212)")
        self.temp_card = self._create_sensor_card("Temperature", "temp_value", "°C", "rgb(255,87,34)")
        self.status_card = self._create_status_card()

        cards_layout.addWidget(self.lux_card)
        cards_layout.addWidget(self.accel_card)
        cards_layout.addWidget(self.temp_card)
        cards_layout.addWidget(self.status_card)
        main_layout.addWidget(cards_widget)

        plots_widget = QtWidgets.QWidget()
        plots_layout = QtWidgets.QGridLayout(plots_widget)
        plots_layout.setSpacing(10)

        pg.setConfigOptions(antialias=True)
        self.plot_lux = pg.PlotWidget(title="Illuminance (Lux)")
        self.plot_lux.showGrid(x=True, y=True)
        self.curve_lux = self.plot_lux.plot(pen=pg.mkPen(width=2))
        self.plot_lux.setYRange(0, 1000)

        self.plot_accel = pg.PlotWidget(title="Acceleration (m/s²)")
        self.plot_accel.showGrid(x=True, y=True)
        self.curve_accel = self.plot_accel.plot(pen=pg.mkPen(width=2))
        self.plot_accel.setYRange(-20, 20)

        self.plot_temp = pg.PlotWidget(title="Temperature (°C)")
        self.plot_temp.showGrid(x=True, y=True)
        self.curve_temp = self.plot_temp.plot(pen=pg.mkPen(width=2))
        self.plot_temp.setYRange(-10, 60)

        plots_layout.addWidget(self.plot_lux, 0, 0)
        plots_layout.addWidget(self.plot_accel, 0, 1)
        plots_layout.addWidget(self.plot_temp, 1, 0, 1, 2)
        plots_widget.setMinimumHeight(360)
        main_layout.addWidget(plots_widget)

        controls_widget = QtWidgets.QWidget()
        controls_layout = QtWidgets.QHBoxLayout(controls_widget)
        controls_layout.setSpacing(10)
        reset_btn = QtWidgets.QPushButton("Reset Data")
        reset_btn.clicked.connect(self._reset_data)
        export_btn = QtWidgets.QPushButton("Export Data")
        export_btn.clicked.connect(self._export_data)
        controls_layout.addWidget(reset_btn)
        controls_layout.addWidget(export_btn)
        controls_layout.addStretch()
        main_layout.addWidget(controls_widget)

        self.setStyleSheet('''
            QMainWindow { background-color: #0f0f0f; color: #ffffff; }
            QWidget { background-color: transparent; }
            QLabel { color: #c8c8c8; }
            QGroupBox { background-color: #191919; border: 1px solid #3c3c3c; border-radius: 6px; padding: 8px; }
            QPushButton { background-color: rgba(0,112,243,0.4); color: white; border-radius: 6px; padding: 6px 12px; }
            QPushButton:hover { background-color: rgba(0,112,243,0.6); }
        ''')

    def _create_sensor_card(self, title, value_tag, unit, color_str):
        box = QtWidgets.QGroupBox()
        box.setFixedSize(280, 120)
        layout = QtWidgets.QVBoxLayout(box)
        title_label = QtWidgets.QLabel(title)
        title_label.setStyleSheet('color: #c8c8c8; font-weight:600;')
        layout.addWidget(title_label)
        layout.addSpacing(4)
        h = QtWidgets.QWidget()
        hl = QtWidgets.QHBoxLayout(h)
        self_val = QtWidgets.QLabel("0.0")
        self_val.setObjectName(value_tag)
        self_val.setStyleSheet(f'font-size:20px; color: {color_str};')
        unit_label = QtWidgets.QLabel(unit)
        unit_label.setStyleSheet('color: #999999;')
        hl.addWidget(self_val)
        hl.addWidget(unit_label)
        hl.addStretch()
        layout.addWidget(h)
        return box

    def _create_status_card(self):
        box = QtWidgets.QGroupBox()
        box.setFixedSize(280, 150)
        layout = QtWidgets.QVBoxLayout(box)
        title = QtWidgets.QLabel("System Status")
        title.setStyleSheet('color:#c8c8c8; font-weight:600;')
        layout.addWidget(title)
        layout.addSpacing(6)
        h = QtWidgets.QWidget()
        hl = QtWidgets.QHBoxLayout(h)
        self.status_indicator = QtWidgets.QLabel("●")
        self.status_indicator.setStyleSheet('color: rgb(255,100,100); font-size:18px;')
        self.status_text = QtWidgets.QLabel("Disconnected")
        self.status_text.setStyleSheet('color:#c8c8c8;')
        hl.addWidget(self.status_indicator)
        hl.addWidget(self.status_text)
        hl.addStretch()
        layout.addWidget(h)
        self.last_update_label = QtWidgets.QLabel("Last Update: Never")
        self.last_update_label.setStyleSheet('color:#999999;')
        layout.addWidget(self.last_update_label)
        return box

    def _update_gui(self):
        lux_lbl = self.findChild(QtWidgets.QLabel, "lux_value")
        accel_lbl = self.findChild(QtWidgets.QLabel, "accel_value")
        temp_lbl = self.findChild(QtWidgets.QLabel, "temp_value")

        if lux_lbl:
            lux_lbl.setText(f"{self.current_values['lux']:.1f}")
        if accel_lbl:
            accel_lbl.setText(f"{self.current_values['acceleration']:.2f}")
        if temp_lbl:
            temp_lbl.setText(f"{self.current_values['temperature']:.1f}")

        if self.is_connected:
            self.status_indicator.setStyleSheet('color: rgb(100,255,100); font-size:18px;')
            self.status_text.setText("Connected")
        else:
            self.status_indicator.setStyleSheet('color: rgb(255,100,100); font-size:18px;')
            self.status_text.setText("Disconnected")

        self.last_update_label.setText(f"Last Update: {self.last_update}")

        if len(self.time_data) > 1:
            t = list(self.time_data)
            self.curve_lux.setData(t, list(self.lux_data))
            self.curve_accel.setData(t, list(self.accel_data))
            self.curve_temp.setData(t, list(self.temp_data))

        if hasattr(self, "accel_page"):
            self.accel_page.set_accel(self.current_values['acceleration'], 0, 0)
        if hasattr(self, "light_page"):
            self.light_page.set_lux(self.current_values['lux'])
        if hasattr(self, "temp_page"):
            self.temp_page.set_temp(self.current_values['temperature'])

    def _reset_data(self):
        self.lux_data.clear()
        self.accel_data.clear()
        self.temp_data.clear()
        self.time_data.clear()

    def _export_data(self):
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"can_bus_data_{timestamp}.csv"
            with open(filename, 'w') as f:
                f.write("Time,Lux,Acceleration,Temperature\n")
                for i in range(len(self.time_data)):
                    f.write(f"{self.time_data[i]:.2f},{self.lux_data[i]:.2f},{self.accel_data[i]:.2f},{self.temp_data[i]:.2f}\n")
            QtWidgets.QMessageBox.information(self, "Export", f"Data exported to {filename}")
        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "Export error", str(e))

    def closeEvent(self, event: QtGui.QCloseEvent) -> None:
        self.running = False
        event.accept()

if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    QtCore.QCoreApplication.setAttribute(QtCore.Qt.AA_EnableHighDpiScaling, True)
    QtCore.QCoreApplication.setAttribute(QtCore.Qt.AA_UseHighDpiPixmaps, True)
    win = ModernCANBusHMI()
    win.show()
    sys.exit(app.exec())

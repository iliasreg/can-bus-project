from PySide6 import QtCore, QtWidgets, QtOpenGLWidgets
from OpenGL.GL import *
from OpenGL.GLU import *

class GLWidget(QtOpenGLWidgets.QOpenGLWidget):
    def __init__(self):
        super().__init__()
        self.xRot = 0
        self.yRot = 0
        self.zRot = 0
        self.accel = [0, 0, 0]
        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.updateRotation)
        self.timer.start(30)

    def set_accel(self, x, y, z):
        self.accel = [x, y, z]

    def updateRotation(self):
        ax, ay, az = self.accel
        self.xRot += ax * 2
        self.yRot += ay * 2
        self.zRot += az * 2
        self.update()

    def initializeGL(self):
        glClearColor(0.07, 0.07, 0.07, 1.0)
        glEnable(GL_DEPTH_TEST)
        glEnable(GL_CULL_FACE)

    def resizeGL(self, w, h):
        glViewport(0, 0, w, h)
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        gluPerspective(45.0, w / h if h != 0 else 1.0, 0.1, 100.0)
        glMatrixMode(GL_MODELVIEW)

    def paintGL(self):
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glLoadIdentity()
        glTranslatef(0.0, 0.0, -6.0)
        glRotatef(self.xRot, 1.0, 0.0, 0.0)
        glRotatef(self.yRot, 0.0, 1.0, 0.0)
        glRotatef(self.zRot, 0.0, 0.0, 1.0)
        self.drawCube()

    def drawCube(self):
        glBegin(GL_QUADS)
        glColor3f(0.0, 0.74, 0.83)
        glVertex3f(1,1,-1); glVertex3f(-1,1,-1); glVertex3f(-1,1,1); glVertex3f(1,1,1)
        glColor3f(0.0,0.6,0.7)
        glVertex3f(1,-1,1); glVertex3f(-1,-1,1); glVertex3f(-1,-1,-1); glVertex3f(1,-1,-1)
        glColor3f(0.0,0.8,0.85)
        glVertex3f(1,1,1); glVertex3f(-1,1,1); glVertex3f(-1,-1,1); glVertex3f(1,-1,1)
        glColor3f(0.0,0.5,0.6)
        glVertex3f(1,-1,-1); glVertex3f(-1,-1,-1); glVertex3f(-1,1,-1); glVertex3f(1,1,-1)
        glColor3f(0.0,0.7,0.8)
        glVertex3f(-1,1,1); glVertex3f(-1,1,-1); glVertex3f(-1,-1,-1); glVertex3f(-1,-1,1)
        glColor3f(0.0,0.7,0.8)
        glVertex3f(1,1,-1); glVertex3f(1,1,1); glVertex3f(1,-1,1); glVertex3f(1,-1,-1)
        glEnd()

class AccelerationPage(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        layout = QtWidgets.QHBoxLayout(self)
        self.side = QtWidgets.QGroupBox("Acceleration Data")
        self.side.setFixedWidth(280)
        v = QtWidgets.QVBoxLayout(self.side)
        self.x_label = QtWidgets.QLabel("X: 0.0")
        self.y_label = QtWidgets.QLabel("Y: 0.0")
        self.z_label = QtWidgets.QLabel("Z: 0.0")
        self.magnitude = QtWidgets.QLabel("Magnitude: 0.0 m/s²")
        for lbl in [self.x_label, self.y_label, self.z_label, self.magnitude]:
            lbl.setStyleSheet("color:#c8c8c8; font-size:16px;")
            v.addWidget(lbl)
        v.addStretch()
        self.gl = GLWidget()
        layout.addWidget(self.side)
        layout.addWidget(self.gl)

    def set_accel(self, x, y, z):
        self.gl.set_accel(x, y, z)
        mag = (x**2 + y**2 + z**2) ** 0.5
        self.x_label.setText(f"X: {x:.2f}")
        self.y_label.setText(f"Y: {y:.2f}")
        self.z_label.setText(f"Z: {z:.2f}")
        self.magnitude.setText(f"Magnitude: {mag:.2f} m/s²")

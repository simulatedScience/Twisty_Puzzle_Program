import sys
from PyQt5 import QtWidgets
from pyqtgraph.Qt import QtCore, QtGui
import pyqtgraph.opengl as gl
import numpy as np

class ExampleApp(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()

        # Create main window layout
        self.central_widget = QtWidgets.QWidget()
        self.setCentralWidget(self.central_widget)
        layout = QtWidgets.QVBoxLayout()
        self.central_widget.setLayout(layout)

        # Add 3D graphics view
        self.view = gl.GLViewWidget()
        layout.addWidget(self.view)

        # Create a button
        self.button = QtWidgets.QPushButton("Change Color")
        layout.addWidget(self.button)
        self.button.clicked.connect(self.on_button_clicked)

        # Add a colored cube
        self.cube = gl.GLBoxItem(glOptions="opaque", color=(0, 255, 0, 255))
        self.cube.setColor(QtGui.QColor(255, 0, 0, 255))
        self.cube.setDrawMode('faces')
        self.cube.translate(0, 2, 0)
        self.view.addItem(self.cube)

        # Add a colored sphere
        md = gl.MeshData.sphere(rows=10, cols=20)
        self.sphere = gl.GLMeshItem(meshdata=md, smooth=True, shader='shaded', drawFaces=True)
        self.sphere.setColor(QtGui.QColor(0, 0, 255))
        self.sphere.translate(3, 0, 5)
        self.view.addItem(self.sphere)
        
        # make bg grey
        self.view.setBackgroundColor(QtGui.QColor(100, 100, 100))
        
        # draw x y z axis
        self.axis = gl.GLAxisItem(glOptions="opaque")
        self.view.addItem(self.axis)

    def on_button_clicked(self):
        # Change the color of the cube
        current_color = self.cube.color()
        new_color = QtGui.QColor(np.random.randint(255), np.random.randint(255), np.random.randint(255), 255)
        self.cube.setColor(new_color)
        # update viewport
        self.view.update()
        print(f"changed color from {current_color} to {new_color}")

app = QtWidgets.QApplication(sys.argv)
ex = ExampleApp()
ex.show()
sys.exit(app.exec_())

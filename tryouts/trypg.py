#!/usr/bin/env python
import sys
import pyqtgraph as pg
from PyQt5 import QtWidgets, QtGui, QtCore
import pyqtgraph.parametertree.parameterTypes as pTypes
from pyqtgraph.parametertree import Parameter, ParameterTree

class MainWindow(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        # Main UI code goes here
        
        self.setWindowTitle('Trying out Parameters and Trees from pyqtgraph')
        
        layout = QtGui.QGridLayout(self)
        layout.addWidget(QtGui.QLabel("Working with Parameters and Trees"), 0,  0, 1, 1)

        self.params = [
            {'name': 'Segment', 'type': 'group',
             'removable': True, 'renamable': True, 'children': [
                {'name': 'Heart Rate Targets', 'type': 'group', 'children': [
                    {'name': 'High', 'type': 'int', 'suffix': 'bpm', 'value': 140},
                    {'name': 'Low', 'type': 'int', 'suffix': 'bpm', 'value': 135}]
                },
                {'name': 'Timing', 'type': 'group', 'children': [
                    {'name': 'Warm', 'type': 'float', 'siPrefix': True, 'suffix': 's', 'value': 300},
                    {'name': 'Work', 'type': 'int', 'suffix': 's', 'value': 30},
                    {'name': 'Cool', 'type': 'int', 'suffix': 's', 'value': 200},
                    {'name': 'Repeat', 'type': 'int', 'value': 1}]
                }]
            },
            {'name': 'Add Segment', 'type': 'action'}
        ]
        self.pTree = Parameter.create(name='Session Parameters', type='group', children=self.params)
        self.pTree.param('Add Segment').sigActivated.connect(self.addSegment)
        
        self.pTreeWidget = ParameterTree()
        self.pTreeWidget.setParameters(self.pTree, showTop=False)
        layout.addWidget(self.pTreeWidget, 1, 0, 1, 1) 

        # End main UI code
        self.show()
        self.resize(400, 800)
        
    def addSegment(self):
        self.pTree.insertChild(len(self.pTree.children())-1,
            {
                'name': 'Segment',
                'type': 'str',
                'value': 'Added',
                'renamable': True,
                'removable': True
            },
            autoIncrementName=True
        )
                
if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    mw = MainWindow()
    sys.exit(app.exec())

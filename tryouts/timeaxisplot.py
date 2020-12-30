from PyQt5.QtWidgets import QWidget, QGridLayout
import pyqtgraph as pg
from timeaxisutils import TimeAxisItem, timestamp


class ExampleTimeAxisPlot(QWidget):
    def __init__(self, parent=None):
        QWidget.__init__(self, parent)
        self.plot = pg.PlotWidget(
            title="Example plot",
            labels={'left': 'Reading / mV'},
            axisItems={'bottom': TimeAxisItem(orientation='bottom')}
        )
        self.plot.setYRange(0, 5000)
        self.plot.setXRange(timestamp(), timestamp() + 100)
        self.plot.showGrid(x=True, y=True)
        self.plotCurve = self.plot.plot(pen='y')
        self.plotData = {'x': [], 'y': []}

    def updatePlot(self, newValue):
        self.plotData['y'].append(newValue)
        self.plotData['x'].append(timestamp())
        self.plotCurve.setData(self.plotData['x'], self.plotData['y'])

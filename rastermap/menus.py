from PyQt5 import QtGui, QtCore, QtWidgets
import pyqtgraph as pg
import numpy as np
from . import io

# ------ MENU BAR -----------------
def mainmenu(parent): 
    loadMat =  QtGui.QAction("&Load data", parent)
    loadMat.setShortcut("Ctrl+L")
    loadMat.triggered.connect(lambda: io.load_mat(parent, name=None))
    parent.addAction(loadMat)
    
    # load processed data
    loadProc = QtGui.QAction("&Load processed data", parent)
    loadProc.setShortcut("Ctrl+P")
    loadProc.triggered.connect(lambda: io.load_proc(parent, name=None))
    parent.addAction(loadProc)
    
    # export figure
    exportFig = QtGui.QAction("Export as image (svg)", parent)
    exportFig.triggered.connect(export_fig)
    exportFig.setEnabled(True)
    parent.addAction(exportFig)

    # make mainmenu!
    main_menu = parent.menuBar()
    file_menu = main_menu.addMenu("&File")
    file_menu.addAction(loadMat)
    file_menu.addAction(loadProc)
    file_menu.addAction(exportFig)

def export_fig(parent):
    parent.win.scene().contextMenuItem = parent.p0
    parent.win.scene().showExportDialog()


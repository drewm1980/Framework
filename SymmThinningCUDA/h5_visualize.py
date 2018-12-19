#!/usr/bin/env python
#
# sudo apt-get install python python-numpy python-opengl python-qt4 python-qt4-gl

from __future__ import print_function

import h5py
import numpy as np
import sys
import os
import time

from pyqtgraph.Qt import QtCore, QtGui
import pyqtgraph as pg
import pyqtgraph.opengl as gl

color=(1,1,1,0.4)
size=0.4
#filename="./isthmus_skeletonization/SymmThinningCUDA/SymmThinningCUDA/originalH5/0.h5"
dimensions=int(sys.argv[1])
directories=sys.argv[2:]

print("using dimension from arg2: \"%sx%sx%s\""%(dimensions,dimensions,dimensions))
print("reading directories:\n\t%s\n"%"\n\t".join(directories))

dirindex = 0
data = []
def plot():
    global dirindex
    global data
    compactIjkVec = []
    zoffset=0
    z=0
    currentdir = directories[dirindex]
    print("currentdir:",currentdir)
    files = [f for f in os.listdir(currentdir) if f.endswith('.h5')]

    if not files or len(files)<=0:
        print("error reading directory ",currentdir)
        print(os.listdir(currentdir))
        return

    files.sort()
    for filename in files:
        print("file",currentdir+"/"+filename)
        try:
            f1 = h5py.File(currentdir+'/'+filename,'r+')
        except Exception as error:
            print("error h5py open", error)
            continue
        zoffset=z
        for s in f1:
            shape = f1[s].shape
            #print("set",s, "shape", shape, "zoffset", zoffset)
            z=zoffset+int(s)
            for ijk in f1[s][0]:
                x = ijk % dimensions
                y = ijk / dimensions
                #print("%d x=%d y=%d z=%d"%(ijk,x,y,z),end=",  ")
                compactIjkVec.append((x,y,z))
            #print()
            #break
        f1.close()

    data = np.array(compactIjkVec)
    try:
        plt.setData(pos=data, color=color)
    except Exception as error:
        print("error plt", error)

    # prep next dir
    dirindex = (dirindex + 1) % len(directories)


# run once so we are ready to load qt
plot()


#sys.exit()

# ## build a QApplication before building other widgets
# from pyqtgraph.Qt import QtCore, QtGui
# import pyqtgraph as pg
# import pyqtgraph.opengl as gl
# app = QtGui.QApplication([])
# w = gl.GLViewWidget()
# w.show()
# w.setWindowTitle('hdf5 test')
# w.setCameraPosition(distance=40)
# g = gl.GLGridItem()
# #g.scale(2,2,1)
# w.addItem(g)
# #
# plt = gl.GLScatterPlotItem(pos=data, color=(1,1,1,1.0), size=0.1, pxMode=True)
# #plt.translate(-128,-128 ,0)
# w.addItem(plt)




# ## build a QApplication before building other widgets


## make a widget for displaying 3D objects

pg.mkQApp()

view = gl.GLViewWidget()
view.setCameraPosition(distance=600)
view.show()

## create three grids, add each to the view
xgrid = gl.GLGridItem()
# ygrid = gl.GLGridItem()
# zgrid = gl.GLGridItem()
view.addItem(xgrid)
# view.addItem(ygrid)
# view.addItem(zgrid)

## rotate x and y grids to face the correct direction
xgrid.rotate(90, 0, 1, 0)
# ygrid.rotate(90, 1, 0, 0)

## scale each grid differently
xgrid.scale(30, 30, 0)
# ygrid.scale(30, 30, 0)
# zgrid.scale(30, 30, 0)

plt = gl.GLScatterPlotItem(pos=data, color=color, size=size, pxMode=False)
# plt.rotate(90,0,1,0)
# plt.rotate(90,1,0,0)
# plt.translate(0,0,-(dimensions/2))
# plt.translate(0,-200,0)
plt.translate(0,-(dimensions/2),0)
plt.translate(-(dimensions/2),0,0)
plt.translate(0,0,-(dimensions/4))

view.addItem(plt)


if len(directories) > 1:
    t = QtCore.QTimer()
    t.timeout.connect(plot)
    t.start(500)

## Start Qt event loop unless running in interactive mode.
if __name__ == '__main__':
    import sys
    if (sys.flags.interactive != 1) or not hasattr(QtCore, 'PYQT_VERSION'):
        QtGui.QApplication.instance().exec_()

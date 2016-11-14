import numpy as np
import matplotlib.pyplot as pl

import smq.logging as log

# check pandas, seaborne

class PlotTimeseries(object):
    def __init__(self, conf):
        print "conf", conf

    def run(self):
        print "log.h5file", log.h5file
        print "dir(log.h5file)", dir(log.h5file)
        print "blub", type(log.h5file.root.item_pm_data)
        # for item in log.h5file.root.item_pm_data:
        # print type(item)
        pl.ioff()
        pl.plot(log.h5file.root.item_pm_data)
        pl.show()

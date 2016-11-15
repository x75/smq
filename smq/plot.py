import numpy as np
import matplotlib.pyplot as pl

import smq.logging as log

# check pandas, seaborne

class PlotTimeseries(object):
    def __init__(self, conf):
        print "conf", conf

    def run(self):
        print "log.h5file", log.h5file
        # print "dir(log.h5file)", dir(log.h5file)
        # print "blub", type(log.h5file.root.item_pm_data)
        # for item in log.h5file.root.item_pm_data:
        # print type(item)
        # print "log.h5file.root.item_pm_data", log.h5file.root.item_pm_data.read()
        data = log.h5file.root.item_pm_data.read()
        
        pl.ioff()
        pl.suptitle("Experiment %s" % (log.h5file.title))
        pl.subplot(121)
        pl.plot(data.T)
        pl.xlabel("t [steps]")
        pl.legend(["acc_p", "vel_e", "vel_", "pos_", "vel_goal", "dist_goal", "acc_pred", "m"])
        pl.subplot(122)
        pl.hist(data.T, bins=20, orientation="horizontal")
        pl.xlabel("counts")
        pl.show()

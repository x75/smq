import numpy as np
import matplotlib.pyplot as pl
import pandas as pd
import seaborn as sns

import smq.logging as log

# check pandas, seaborne

class PlotTimeseries(object):
    def __init__(self, conf):
        print "conf", conf
        self.type = conf["type"]

    def run(self):
        print "log.h5file", log.h5file
        pl.ioff()
        # print "dir(log.h5file)", dir(log.h5file)
        # print "blub", type(log.h5file.root.item_pm_data)
        # for item in log.h5file.root.item_pm_data:
        # print type(item)
        # print "log.h5file.root.item_pm_data", log.h5file.root.item_pm_data.read()

        # df = log.log_lognodes["pm"]
        # g = sns.FacetGrid(df, col=list(df.columns))
        # g.map(pl.plot, )

        
        data = log.h5file.root.item_pm_data.read()
        data = log.log_lognodes["pm"].values.T
        columns = log.log_lognodes["pm"].columns
        print "data.shape", data.shape
        pl.suptitle("Experiment %s" % (log.h5file.title))
        for i,datum in enumerate(data):
            pl.subplot(data.shape[0], 2, (i*2)+1)
            # pl.title(columns[i])
            # sns.timeseries.tsplot(datum)
            pl.plot(datum, "k-", alpha=0.5)
            print "columns[i]", type(columns[i])
            pl.legend(["%s" % (columns[i])])
        pl.xlabel("t [steps]")
        # pl.legend(["acc_p", "vel_e", "vel_", "pos_", "vel_goal", "dist_goal", "acc_pred", "m"])
        # pl.subplot(122)
        for i,datum in enumerate(data):
            pl.subplot(data.shape[0], 2, (i*2)+2)
            # print "dataum", datum
            pl.hist(datum, bins=20, orientation="horizontal")
            pl.legend(["%s" % (columns[i])])
        # pl.hist(data.T, bins=20, orientation="horizontal")
        pl.xlabel("counts")
        pl.show()

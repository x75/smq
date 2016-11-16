import numpy as np
import matplotlib.pyplot as pl
import pandas as pd
import seaborn as sns

import smq.logging as log

# check pandas, seaborne
# FIXME: fix hardcoded tablenames

from smq.utils import set_attr_from_dict

class Plot(object):
    def __init__(self, conf):
        self.conf = conf
        set_attr_from_dict(self, conf)

class PlotTimeseries(Plot):
    def __init__(self, conf):
        Plot.__init__(self, conf)
        
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

class PlotTimeseries2D(Plot):
    def __init__(self, conf):
        Plot.__init__(self, conf)

    def run(self):
        df = log.log_lognodes["pm"]
        data = df.values.T
        columns = df.columns
        # print "columns", columns

        pl.ioff() #
        
        if self.type == "pyplot":
            # pl.plot(df["vel0"], df["vel1"], "ko")
            # print df["vel0"].values.dtype
            pl.subplot(131)
            pl.title("state distribution and goal")
            # print df["vel_goal0"].values, df["vel_goal1"].values
            # pl.hist2d(df["vel0"].values, df["vel1"].values, bins=20)
            pl.plot(df["vel_goal0"].values[0], df["vel_goal1"].values[0], "ro", markersize=16, alpha=0.5)
            pl.hexbin(df["vel0"].values, df["vel1"].values, gridsize = 30, marginals=True)
            pl.plot(df["vel0"].values, df["vel1"].values, "k-", alpha=0.25, linewidth=1)
            pl.xlim((-1.2, 1.2))
            pl.ylim((-1.2, 1.2))
            pl.grid()
            pl.colorbar()

            pl.subplot(132)
            pl.title("prediction distribution")
            pl.hexbin(df["acc_pred0"].values, df["acc_pred1"].values, gridsize = 30, marginals=True)
            pl.xlim((-1.2, 1.2))
            pl.ylim((-1.2, 1.2))

            pl.subplot(133)
            pl.title("goal distance distribution")
            pl.hist(df["dist_goal0"].values)

            
            pl.show()
        elif self.type == "seaborn":
            sns.jointplot(x="vel0", y="vel1", data=df)
            # pl.plot(df["vel_goal0"], df["vel_goal1"], "ro")
            pl.show()

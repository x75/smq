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

    def run(self, items):
        self.make_plot(items)

    def make_plot(self, items):
        print "%s.make_plot: implement me" % (self.__class__.__name__)
        
class PlotTimeseries(Plot):
    def __init__(self, conf):
        Plot.__init__(self, conf)

    def run(self, items):
        # how many axes / plotitems
        # configure subplotgrid
        
        tbl_key = items[0].name
        # tbl_key = items[0].conf["name"]
        print "tbl_key", tbl_key
        df = log.log_lognodes[tbl_key]
        
        # data = log.h5file.root.item_pm_data.read()
        # data = log.log_lognodes["pm"].values.T
        # columns = log.log_lognodes["pm"].columns
        
        data = df.values.T
        columns = df.columns

        # print "data.shape", data.shape

        pl.ioff()
        # create figure
        fig = pl.figure()
        fig.suptitle("Experiment %s" % (log.h5file.title))
        # fig.suptitle("Experiment %s" % (self.title))
        for i in range(data.shape[0]): # loop over data items
            ax1 = pl.subplot2grid((data.shape[0], 2), (i, 0))
            ax1 = self.make_plot_timeseries(ax1, data[i], columns[i])
            
            ax2 = pl.subplot2grid((data.shape[0], 2), (i, 1)) # second plotgrid column
            ax2 = self.make_plot_histogram(ax2, data[i], columns[i])

        # global for plot, use last axis
        ax1.set_xlabel("t [steps]")
        ax2.set_xlabel("counts")
        
        # fig.show() # this doesn't work
        pl.show()

    def make_plot_timeseries(self, ax, data, columns):
        ax.plot(data, "k-", alpha=0.5)
        # print "columns[i]", type(columns[i])
        ax.legend(["%s" % (columns)])
        return ax

    def make_plot_histogram(self, ax, data, columns):
        ax.hist(data, bins=20, orientation="horizontal")
        ax.legend(["%s" % (columns)])
        # pl.hist(data.T, bins=20, orientation="horizontal")
        return ax
    
    # def make_plot(self, items):
    #     # print "log.h5file", log.h5file
    #     # print "dir(log.h5file)", dir(log.h5file)
    #     # print "blub", type(log.h5file.root.item_pm_data)
    #     # for item in log.h5file.root.item_pm_data:
    #     # print type(item)
    #     # print "log.h5file.root.item_pm_data", log.h5file.root.item_pm_data.read()

    #     # df = log.log_lognodes["pm"]
    #     # g = sns.FacetGrid(df, col=list(df.columns))
    #     # g.map(pl.plot, )

        
    #     # print "data.shape", data.shape
    #     for i,datum in enumerate(data):
    #         pl.subplot(data.shape[0], 2, (i*2)+1)
    #         # pl.title(columns[i])
    #         # sns.timeseries.tsplot(datum)
    #         pl.plot(datum, "k-", alpha=0.5)
    #         # print "columns[i]", type(columns[i])
    #         pl.legend(["%s" % (columns[i])])
    #     pl.xlabel("t [steps]")
    #     # pl.legend(["acc_p", "vel_e", "vel_", "pos_", "vel_goal", "dist_goal", "acc_pred", "m"])
    #     # pl.subplot(122)
    #     for i,datum in enumerate(data):
    #         pl.subplot(data.shape[0], 2, (i*2)+2)
    #         # print "dataum", datum
    #         pl.hist(datum, bins=20, orientation="horizontal")
    #         pl.legend(["%s" % (columns[i])])
    #     # pl.hist(data.T, bins=20, orientation="horizontal")
    #     pl.xlabel("counts")
    #     pl.show()

class PlotTimeseries2D(Plot):
    def __init__(self, conf):
        Plot.__init__(self, conf)

    def run(self, items):
        # FIXME: assuming len(items) == 1, which might be appropriate depending on the experiment
        if items[0].dim_s_motor > 2:
            print "more than two dimensions in data, plot is going to be incomplete"
            return
        tbl_key = items[0].name
        # tbl_key = items[0].conf["name"]
        print "%s.run: tbl_key = %s" % (self.__class__.__name__, tbl_key)
        df = log.log_lognodes[tbl_key]
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
            # pl.xlim((-1.2, 1.2))
            # pl.ylim((-1.2, 1.2))
            pl.grid()
            pl.colorbar()

            pl.subplot(132)
            pl.title("prediction distribution")
            pl.hexbin(df["acc_pred0"].values, df["acc_pred1"].values, gridsize = 30, marginals=True)
            pl.xlim((-1.2, 1.2))
            pl.ylim((-1.2, 1.2))
            pl.colorbar()

            pl.subplot(133)
            pl.title("goal distance distribution")
            pl.hist(df["dist_goal0"].values)

            
            pl.show()
        elif self.type == "seaborn":
            print "goal", df["vel_goal0"][0], df["vel_goal1"][0]
            ax = sns.jointplot(x="vel0", y="vel1", data=df)
            print "ax", dir(ax)
            ax.ax_joint.plot(df["vel_goal0"][0], df["vel_goal1"][0], "ro", alpha=0.5)
            # pl.plot(df["vel_goal0"], df["vel_goal1"], "ro")
            pl.show()


def get_data_from_item_log(items):
    tbl_key = items[0].name
    # print "%s.run: tbl_key = %s" % (self.__class__.__name__, tbl_key)
    print "plot.get_data_from_item_log: tbl_key = %s" % (tbl_key)
    df = log.log_lognodes[tbl_key]
    data = df.values.T
    columns = df.columns
    return tbl_key, df, data, columns
            
class PlotTimeseriesND(Plot):
    def __init__(self, conf):
        Plot.__init__(self, conf)

    def run(self, items):
        pl.ioff()

        tbl_key, df, data, columns = get_data_from_item_log(items)
        
        # transform df to new df
        if hasattr(self, "cols"):
            cols = self.cols
        else:
            cols  = ["vel%d" % (i) for i in range(items[0].dim_s_motor)]
            cols += ["acc_pred%d" % (i) for i in range(items[0].dim_s_motor)]
        df2 = df[cols]

        # goal columns
        if not hasattr(self, "cols_goal_base"):
            setattr(self, "cols_goal_base", "vel_goal")
        
        # pp = sns.pairplot(df2)

        # for i in range(3):
        #     for j in range(3): # 1, 2; 0, 2; 0, 1
        #         if i == j:
        #             continue
        #         pp.axes[i,j].plot(df["vel_goal%d" % i][0], df["vel_goal%d" % j][0], "ro", alpha=0.5)
                
        
        # # print pp.axes
        # # for axset in pp.axes:
        # #     print "a", axset
        # #     for 
        # # print "dir(pp)", dir(pp)
        
        # pl.show()


        g = sns.PairGrid(df2)
        g.map_diag(pl.hist)
        g.map_offdiag(pl.hexbin, cmap="gray", gridsize=30);

        # print "dir(g)", dir(g)
        # print g.diag_axes
        # print g.axes
        for i in range(items[0].dim_s_motor):
            for j in range(items[0].dim_s_motor): # 1, 2; 0, 2; 0, 1
                if i == j:
                    continue
                # column gives x axis, row gives y axis, thus need to reverse the selection for plotting goal
                g.axes[i,j].plot(df["%s%d" % (self.cols_goal_base, j)], df["%s%d" % (self.cols_goal_base, i)], "ro", alpha=0.5)
                
        pl.show()

        pl.hist(df["dist_goal0"].values, bins=20)
        pl.show()

class PlotExplautoSimplearm(Plot):
    def __init__(self, conf):
        Plot.__init__(self, conf)

    def make_plot(self, items):
        print "items", items
        pl.ioff()

        tbl_key, df, data, columns = get_data_from_item_log(items)
        motors = df[["j_ang%d" % i for i in range(items[0].dim_s_motor)]]
        goals  = df[["j_ang_goal%d" % i for i in range(items[0].dim_s_motor)]]
        # print "df", motors, columns #, df
        
        fig = pl.figure()
        for i,item in enumerate(items):
            # fig.suptitle("Experiment %s" % (log.h5file.title))
            ax = fig.add_subplot(len(items), 1, i+1)
            for m in motors.values:
                # print "m", m
                item.env.env.plot_arm(ax = ax, m = m)
            print "plot goal", goals.values[0]
            item.env.env.plot_arm(ax = ax, m = goals.values[0], c="r")
        pl.show()
        

################################################################################
class PlotTimeseries2(Plot):
    def __init__(self, conf):
        Plot.__init__(self, conf)

    def run(self, items):
        # how many axes / plotitems
        # configure subplotgrid
        
        tbl_key = items[0].name
        # tbl_key = items[0].conf["name"]
        print "tbl_key", tbl_key
        df = log.log_lognodes[tbl_key]
        
        # data = log.h5file.root.item_pm_data.read()
        # data = log.log_lognodes["pm"].values.T
        # columns = log.log_lognodes["pm"].columns
        
        data = df.values.T
        columns = df.columns

        # print "data.shape", data.shape

        pl.ioff()
        # create figure
        fig = pl.figure()
        fig.suptitle("Experiment %s, module %s" % (self.title, tbl_key))
        for i in range(data.shape[0]): # loop over data items
            ax1 = pl.subplot2grid((data.shape[0], 2), (i, 0))
            ax1 = self.make_plot_timeseries(ax1, data[i], columns[i])
            
            ax2 = pl.subplot2grid((data.shape[0], 2), (i, 1)) # second plotgrid column
            ax2 = self.make_plot_histogram(ax2, data[i], columns[i])

        # global for plot, use last axis
        ax1.set_xlabel("t [steps]")
        ax2.set_xlabel("counts")
        
        # fig.show() # this doesn't work
        pl.show()

    def make_plot_timeseries(self, ax, data, columns):
        ax.plot(data, "k-", alpha=0.5)
        # print "columns[i]", type(columns[i])
        ax.legend(["%s" % (columns)])
        return ax

    def make_plot_histogram(self, ax, data, columns):
        ax.hist(data, bins=20, orientation="horizontal")
        ax.legend(["%s" % (columns)])
        # pl.hist(data.T, bins=20, orientation="horizontal")
        return ax

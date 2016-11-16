"""logging lib for smq"""

# please satisfy all logging needs for smq

# 0. fixed length
# 1. synchronous time (hm...)
# 2. numpy arrays
# 3. hdf5 / pytables
# 4. python logging?

# implementations in smp
# - smp/smpblocks/smpblock/blogging.py
#   - BlockLogger (nay)
#   - x v2 logger (yay)
# - paparazzi/sw/ground_segment/python/paramopt.py

import tables as tb

# declare global h5 file handle
h5file = 0
# is log inited?
# loginit = False 
loginit = True
lognodes = {}

################################################################################
# raw tables logging
def init_log2(config):
    """second attempt at log init function: called from Blockspy3 init, triggered by topblock arg of Blockspy3"""
    global h5file, loginit, lognodes
    # ts = datetime.datetime.now().strftime("%Y%m%d-%H%M%S-%f")
    # experiment_name = config.keys()[0]
    experiment = "%s" % (config["id"]) # , ts)
    tblfile = "data/%s.h5" % (experiment)
    h5file  = tb.open_file(tblfile, mode = "w", title = "%s" % (experiment))
    root = h5file.root
    storage_version = "v2"

    # create VLArray for storing the graph configuration
    conf_array = h5file.create_vlarray(root, 'conf', tb.VLStringAtom(),
                               "Variable Length Config String")
    conf_array.append(str(config))
    # FIXME: log git commit

    # create topblock array
    # a = tb.Float64Atom()
    # lognodes[parent.id] = h5file.create_earray(root, "%s_obuf" % (parent.id), a, (parent.odim, 0))
    # # create arrays for each node's data
    # for nodek, nodev in nodes.items():
    #     print("init_log: node", nodek)
    #     a = tb.Float64Atom()
    #     # node_fieldkeys = 
    #     # for node_fieldkey in ["%s_%03d" % (nodek, i) for i in range(nodev.odim)]:
    #     #     tdef[node_fieldkey] = tb.Float32Col()
    #     # tdef[nodek] = tb.Float32Col(shape=(nodev.odim, 1))
    #     # return tdef
    #     lognodes[nodev.id] = h5file.create_earray(root, "%s_obuf" % (nodev.id), a, (nodev.odim, 0))
    # loginit = True # this doesn't work yet persistently, why?
    loginit = True
    print("initlog done")

def init_log2_block(tbl_name, tbl_dim, tbl_columns = None):
    print("init_log2_block", tbl_name, tbl_dim)
    global loginit, h5file, lognodes
    if loginit:
        a = tb.Float64Atom()
        lognodes[tbl_name] = h5file.create_earray(h5file.root, "item_%s_data" % (tbl_name), a, (tbl_dim, 0))
        
def log(nodeid, data):
    """Global logging method, like in python logging: take data, write into corresponding array"""
    # FIXME: make a dummy log method an overwrite it on loginit with the real function body?
    # print("id: %s, data: %s" % (id, str(data)[:60]))
    # print("log")
    # print("lognode", lognodes[nodeid])
    # print("data shape", data.shape)
    lognodes[nodeid].append(data)

################################################################################
# pandas based logging
import pandas as pd

log_store = 0
log_lognodes = {}
log_lognodes_idx = {}

def init_log3(config):
    global log_store
    experiment = "%s" % (config["id"])
    log_store = pd.HDFStore("data/%s_pd.h5" % (experiment))

def init_log3_block(tbl_name, tbl_dim, tbl_columns = None, numsteps=100):
    global log_store, log_lognodes
    print "adding %s to log_lognodes with columns %s" % (tbl_name, tbl_columns)
    log_lognodes[tbl_name] = pd.DataFrame(columns=tbl_columns, index = range(numsteps))
    log_lognodes_idx[tbl_name] = 0

def log3(nodeid, data):
    global log_lognodes, log_lognodes_idx
    print "data.shape", data.flatten().shape, log_lognodes_idx[nodeid]
    log_lognodes[nodeid].loc[log_lognodes_idx[nodeid]] = data.flatten()
    # log_lognodes[nodeid].loc[0] = 1
    # print "log_lognodes[nodeid]", log_lognodes[nodeid].loc[0]
    log_lognodes_idx[nodeid] += 1

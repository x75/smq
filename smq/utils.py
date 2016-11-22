"""smq util functions"""

import time
import numpy as np

def get_items(items_conf):
    """generic function creating a list of objects from a config specification
    objects are: analyses, robots, worlds, tasks, losses, ...
    """
    items = []
    for i, item_conf in enumerate(items_conf):
        # instantiate an item of class "class" with the given configuration
        # and append to list
        items.append(item_conf["class"](item_conf))
    # return list
    return items

def get_items2(conf, item = None):
    """generic function creating a list of objects from a config specification
    objects are: analyses, robots, worlds, tasks, losses, ...
    """
    if item is None: return
    items = []
    for i, item_conf in enumerate(conf[item]):
        # instantiate an item of class "class" with the given configuration
        # and append to list
        items.append(item_conf["class"](item_conf, conf["ifs"][i]))
    # return list
    return items

def set_attr_from_dict(obj, dictionary):
    """set attributes of an object with names from the dictionary's keys and their values from the dictionary's values"""
    for k,v in dictionary.items():
        setattr(obj, k, v)
        

def make_column_names_numbered(base = "base", times = 1):
    """create an array of numbered instances of a base string"""
    return ["%s%d" % (base, i) for i in range(times)]

def make_expr_id(name):
    return "%s_%s" % (name, time.strftime("%Y%m%d_%H%M%S"))

def make_robot_name(expr_id, name, number):
    return "%s_%s_%d" % (expr_id, name, number)


################################################################################
# cartesian to polar transformation for n dimensions
def ct_dynamic(r, alpha):
    """alpha: the n-2 values between [0,\pi) and last one between [0,2\pi)
    """
    x = np.zeros(len(alpha) + 1)
    s = 1
    for e, a in enumerate(alpha):
        x[e] = s*np.cos(a)
        s *= np.sin(a)
    x[len(alpha)] = s
    return x*r

def ct_pol2car(r, arr):
    """n-sphere polar to cartesian"""
    a1 = np.array([2*np.pi])
    print "a1.shape= %s, arr.shape = %s"  % (a1.shape, arr.shape)
    a = np.concatenate((a1, arr))
    si = np.sin(a)
    si[0] = 1
    si = np.cumprod(si)
    co = np.cos(a)
    co = np.roll(co, -1)
    return si*co*r

def ct_car2pol(x):
    """n-sphere cartesian to polar, x cartesian column vector"""
    p = np.zeros_like(x)
    r = np.linalg.norm(x)
    p[0] = r
    for i in range(x.shape[0]-1):
        if i == x.shape[0]-2:
            if x[i+1] >= 0:
                phi = np.arccos(x[i] / np.sqrt(np.sum(np.square(x[i:]))))
            elif x[i+1] < 0:
                phi = 2 * np.pi - np.arccos(x[i] / np.sqrt(np.sum(np.square(x[i:]))))
        else:
            phi = np.arccos(x[i] / np.sqrt(np.sum(np.square(x[i:]))))
        p[i+1] = phi

    return p

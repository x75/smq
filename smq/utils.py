"""smq util functions"""

import time

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

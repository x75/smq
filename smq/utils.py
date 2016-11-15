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


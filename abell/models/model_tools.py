def list_stringify(item):
    list_range = len(item)
    for i in range(0, list_range, 1):
        if type(item[i]) is dict:
            dict_stringify(item[i])
        elif type(item[i]) is list:
            list_stringify(item[i])
        else:
            item[i] = str(item[i])

    return item


def dict_stringify(item):
    for key in item:
        if type(item[key]) is dict:
            dict_stringify(item[key])
        elif type(item[key]) is list:
            list_stringify(item[key])
        else:
            item[key] = str(item[key])

    return item


def item_stringify(item_dict):
    """Converts each value in the item dictionary to a string.
    """

    for key in item_dict:
        if type(item_dict[key]) is dict:
            dict_stringify(item_dict[key])

        elif type(item_dict[key]) is list:
            list_stringify(item_dict[key])
        else:
            item_dict[key] = str(item_dict[key])

    return item_dict

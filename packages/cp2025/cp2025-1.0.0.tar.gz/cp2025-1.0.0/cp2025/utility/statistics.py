def mode(array):
    counts = dict()
    for el in array:
        if el not in counts:
            counts[el] = 1
        else:
            counts[el] += 1
    mx_key = array[0]
    for key in counts.keys():
        if counts[key] > counts[mx_key]:
            mx_key = key
    return mx_key
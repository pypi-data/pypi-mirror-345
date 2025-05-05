# mean median mode

def mean(mean_list):
    if len(mean_list) == 1:
        raise Exception('MathError: Must have 2 or more numbers in a list to find mean')
    
    return sum(mean_list) / len(mean_list)


def median(median_list):
    if len(median_list) == 1:
        raise ValueError('MathError: Must have 2 or more numbers in a list to find median')
    
    if len(median_list) % 2 != 0:
        median_list.sort(reverse=True)
        return (median_list[1] / 2) + 1
    else:
        return mean([len(median_list) / 2, (len(median_list) / 2) + 1])

def mode(mode_list):
    if len(mode_list) == 1:
        raise ValueError('MathError: Must have 2 or more numbers in a list to find median')

    return max(mode_list)


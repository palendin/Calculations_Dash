import pandas as pd

#function to get individual set of data from each header for creating a dictionary
def form_array(header, filter_data): 
    data_array = []
    for h in header:
        data_array.append(filter_data[h])   
    return data_array

#function for cumulative calculations for individual run
def cum_calc(data_array):
    array = []
    v = data_array[0] #initial value for the run
    array_length = range(len(data_array))
    for l in array_length:
        if l <  len(array_length): 
            v = v + data_array[l]
            array.append(v)
    return array

def PSA_cum_calc(data_array): #need to adjust PSA array index because NH4 measurement is before the PSA addition
    array = []
    v = data_array[0] #initial value for the run
    array.append(v) #append initial value first.
    array_length = range(len(data_array))
    for l in array_length:
        if l <  len(array_length)-1: #sum to neglect the last day since no PSA added after sampling.
            v = v + data_array[l]
            array.append(v)
    return array

def df_PSA_cum_calc(data_array): #need to adjust PSA array index because NH4 measurement is before the PSA addition
    sum_array = data_array.cumsum()
    sum_array.loc[-1] = 0 #add '0' to first row
    sum_array.index = sum_array.index + 1  # then shifting index
    sum_array = sum_array.sort_index()  # then sorting by index to get proper indexing
    sum_array = sum_array[:-1] #delete last row
    return sum_array
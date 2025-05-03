import numpy as np

def moving_average(data:np.ndarray, half_window:int, min_arr:int, tol:float) -> np.ndarray:
    """Moving average smoothing algorithm.
    An iterative algorithm used to smooth data. Used as a reference point to assess the performance of lowess and rrm. 

    Testing methodology based on: Hen I., Sakov A., Kafkafi N., Golani I., Benjamini Y.
                                  The dynamics of spatial behavior: how can robust smoothing techniques help?
                                  Journal of Neuroscience Methods 133 (2004) 161-172
    
    Parameters
    ----------
    data : numpy.ndarray
        length n array of raw x or y movement data.
    half_window : int
        Half the width of a window of data.
        Each window has width: 2*half_window + 1
    min_arr : int
        The minimum number of frames required for a segment to be classified an arrest.
        There must be at least min_arr frames in a row within tol of each other to register an arrest.
    tol : float
        The max distance between two points that will be considered equal for the sake of identifying arrests. 
    Returns
    -------
    numpy.ndarray
        Data and identified arrest intervals.
    """
    
    n = data.shape[0]
    data_s  = np.zeros(n, dtype = float)
    hw = half_window

    for i in range(n):
        data_s[i] = np.mean(data[max(0, i - hw) : min(n, i + hw + 1)])

    arrests = []
    i = 0
    
    # Iterating over data to identify arrests with length of at least min_arr.
    # Arrests are stored as (start,end) pairs indicating the segment ids of the start and end of the arrest. 
    while i < n:
        start_idx = i
        start = data_s[i]
        seg_len = 1
        for j in range(i+1,n):
            if abs(start - data_s[j]) > tol:
                if seg_len >= min_arr:
                    arrests.append((start_idx + 1,j))
                i = j
                break
            seg_len += 1
            if j == n-1:
                if seg_len >= min_arr:
                    arrests.append((start_idx + 1,j+1))
                i = n
                

    return data_s, arrests

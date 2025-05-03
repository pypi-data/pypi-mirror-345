import numpy as np
import random
import scipy.stats as stats
from types import FunctionType


# Indices for parameters within parameter matrices.
MEAN = 0 # Mean
SD   = 1 # Standard deviation
PROP = 2 # Proportion

def segment_path(data:np.ndarray, arrests:list, half_window:int, log_transform:FunctionType, num_guesses:int, num_iters:int, significance:float, max_k:int, k:int = None):
    """Path segmentation algorithm to categorize smoothed time-series data into segments of lingering and progression.

    Based on: Drai D., Benjamini Y., Golani I.
              Statistical discrimination of natural modes of motion in rat exploratory behavior
              Journal of Neuroscience Methods 96 (2000) 119-131
    
    Parameters
    ----------
    data : numpy.ndarray
        n x 2 array containing smoothed x,y coordinates.
    half_width : int
        Half window length to be used to calculate standard deviations of movement.
    log_transform : FunctionType
        Function (Float -> Float) used to map SDs onto a logarithmic scale for segmentation.
    num_guesses : int
        Number of times EM will be run using different initial guesses.
    num_iters : int
        Number of iterations for the underlying EM algorithm for each initial guess. 
    significance : float
        Alpha value used for a chi squared test to determine the convergence of likelihood improvements.
        If using set number of gaussian movement clusters (k), value is ignored.
    max_k : int
        When using automated calculations of optimal number of movement modes (k),
        function will raise error if no convergence is found after max_k modes.
        If using set number of gaussian movement clusters (k), value is ignored.
    k : int
        Number of movement modes (gaussians) in the gaussian mixture model (GMM).
        For automatic calculation of the optimal k value, use k = None 
        Defaults to None

    Returns
    -------
    numpy.ndarray
        Classified segments.
    """

    # initializing variables
    n = data.shape[0]
    sd = np.zeros(n)
    is_arrest = np.zeros(n)
    hw = half_window
    
    for start,end in arrests:
        is_arrest[start:end+1] = 1

    # Calculate standard deviation for windows centered around each data point.
    for i in range(n):
        if not is_arrest[i]:
            sd[i] = sd_move(data[max(0, i - hw) : min(n, i + hw + 1)])

    # Define segments as intervals between arrests:
    segment_borders = np.diff(np.concatenate(([1],is_arrest,[1])))
    starts = np.array(np.where(segment_borders == -1))
    ends = np.array(np.where(segment_borders == 1))
    segments = np.hstack((starts.T, ends.T - 1))
    
    m = segments.shape[0]

    # If there are no arrests or only arrests then there is only 1 segment/movment type.    
    if m < 2: return np.array([[0, n-1, 0]]) 

    # For each segment we track the maximum standard deviation of all points transformed by a given log function. 
    max_sd = np.zeros(m)

    for i in range(m):
        max_sd[i] = log_transform(max(sd[segments[i,0] : segments[i,1] + 1]))
    
    # Run EM either with fixed number of gaussians or automatic calculation of optimal value.
    if k == None:
        params, _ = em_full_auto(max_sd, num_guesses, num_iters, significance, max_k)
    else:
        params, _ = em_auto(max_sd, k, num_guesses, num_iters)
    
    k = params.shape[0]

    # Edge case for only one movement mode.
    if k == 1:
        return np.append(segments, np.zeros(shape = (m,1)), axis = 1)

    # Using EM generated parameters, determine the threshold values that separate modes of movement.
    threshold = np.zeros(k-1)
    mode = 0

    for sd in np.sort(max_sd):
        if gauss_pdf(sd, params[mode,MEAN], params[mode,SD]) < gauss_pdf(sd, params[mode + 1,MEAN], params[mode + 1,SD]):
            threshold[mode] = sd
            mode += 1
        if mode >= k-1:
            break

    if mode < k-1:
        raise ValueError("Invalid distribution")
    
    # Attribute a mode to each segment according to its log_MaxSD value
    seg_modes = np.zeros(shape = (m,1))

    for i in range(m):
        for j in range(k):
            if j == k-1:
                seg_modes[i] = k-1
                break
            elif max_sd[i] < threshold[j]:
                seg_modes[i] = j 
                break
    
    return np.append(segments, seg_modes, axis = 1)

def sd_move(window:np.ndarray):
    """Auxiliary function for path segmentation which calculates the
    standard deviation of data points from their mean within a window of time.

    Parameters
    ----------
    window : numpy.ndarray
        n x 2 array containing x,y coordinates over a short window of time.
    Returns
    -------
    numpy.ndarray
        SD of distances from the mean point in the window.
    """
    n = window.shape[0]
    mean = np.mean(window,axis=0)
    dist = 0
    
    for point in window:
        dist += np.sum((point - mean)**2)
    
    return np.sqrt(dist/(n-1))

def em(data:np.ndarray, k:int, init_guesses:np.ndarray, num_iters:int):
    """Base expectation maximization algorithm using user provided initial guesses.

    Parameters
    ----------
    data : numpy.ndarray
        array of log modified max standard deviations for each segment.
    k : int
        Number of movement types (gaussians) in the gaussian mixture model (GMM).
    init_guesses : numpy.ndarray
        (k x 3) array of initial guesses for mean, SD, and proportion for each gaussian. 
    num_iters : int
        Number of algorithm iterations. 
    Returns
    -------
    numpy.ndarray
        (k x 3) array of estimated parameters.
    float
        final log likelihood.
    """
    
    params = init_guesses
    n = data.shape[0]
    gamma = np.zeros(shape = (n,k))

    for _ in range(num_iters):
        # Expectation step:
        for i in range(n):
            for j in range(k):
                # Use Bayes theorem to compute the likelyhood that data point i belongs to gaussian j:
                gamma[i,j] = ((params[j,PROP] * gauss_pdf(data[i], params[j,MEAN], params[j,SD])) /
                               np.sum([params[z,PROP] * gauss_pdf(data[i], params[z,MEAN], params[z,SD]) for z in range(k)]))
        # Maximization step:
        for j in range(k):
            # For each gaussian update mean, SD, and proportions based on expected responsibilities
            resp = np.sum(gamma[:,j])
            params[j,MEAN] = np.sum([gamma[i,j] * data[i] for i in range(n)]) / resp
            params[j,SD]   = np.sqrt(np.sum([gamma[i,j] * (data[i] - params[j,MEAN])**2 for i in range(n)]) / resp)
            params[j,PROP] = resp / n
 
    # The log likelihood of the dataset given the parameters estimated is an indicator for
    # how well the gaussian mixture model represents the dataset.
    log_likelihood = np.sum([np.log(np.sum([
        params[j,PROP] * gauss_pdf(data[i], params[j,MEAN], params[j,SD]) 
        for j in range(k)])) for i in range(n)])

    return params, log_likelihood

def em_auto(data:np.ndarray, k:int, num_guesses:int, num_iters:int):
    """Partial automation function for expectation maximization.
    Tests EM for different initial guesses and returns the one with the highest log likelihood. 

    Parameters
    ----------
    data : numpy.ndarray
        array of log modified max standard deviations for each segment.
    k : int
        Number of movement types (gaussians) in the gaussian mixture model (GMM).
    num_guesses : int
        Number of times EM will be run using different initial guesses.   
    num_iters : int
        Number of iterations for the underlying EM algorithm for each initial guess. 
    
    Returns
    -------
    numpy.ndarray
        (k x 3) array of estimated parameters from the best EM iteration.
    float
        final log likelihood of the best EM iteration.
    """

    n = data.shape[0]
    opt_params = None
    opt_likelihood = -np.inf

    for _ in range(num_guesses):
        params = np.zeros(shape = (k,3))
        
        # Generate a random set of proportions for the GMM such that the sum(props) = 1.
        # offset proportions slightly to avoid zero division.
        rand_props = [random.random() + 0.000001 for _ in range(k)]
        prop_sum = np.sum(rand_props)
        params[:,PROP] = [(p / prop_sum) for p in rand_props]

        # Calculate mean/sd for each gaussian by taking the mean/sd
        # of that gaussian's proportion of the sorted dataset.
        sorted_data = np.sort(data)
        start = 0

        for j in range(k):
            end = min(start + int(params[j,PROP] * n), n)
            
            params[j,MEAN] = np.mean(sorted_data[start : end])
            params[j,SD]   = np.std(sorted_data[start : end])
            
            start = end

        # Run EM with generated parameters.
        params, log_likelihood = em(data, k, params, num_iters)

        # If EM produces a better likelihood than all previous iterations, update optimal parameters.
        if log_likelihood > opt_likelihood: 
            opt_params, opt_likelihood = params.copy(), log_likelihood

        # debug code
        # print(f"(k = {k}) opt likelihood: {opt_likelihood:.2f}\t current likelihood: {log_likelihood:.2f}")

    return opt_params, opt_likelihood

def em_full_auto(data:np.ndarray, num_guesses:int, num_iters:int, significance:float, max_k:int):
    """Fully automated version of EM algorithm. 
    Tests em_auto for increasing numbers of gaussians (k) until a requested likelihood is reached. 

    Parameters
    ----------
    data : numpy.ndarray
        array of log modified max standard deviations for each segment.
    num_guesses : int
        Number of times EM will be run using different initial guesses.   
    num_iters : int
        Number of iterations for the underlying EM algorithm for each initial guess. 
    significance : float
        Alpha value used for a chi squared test to determine the convergence of likelihood improvements.
    max_k : int
        Function will raise error if no convergence is found after k = max_k modes.
    
    Returns
    -------
    numpy.ndarray
        (k x 3) array of estimated parameters from the best EM iteration.
    float
        final log likelihood of the best EM iteration.
    """
    
    prev_likelihood = -np.inf
    prev_params = None

    # Test on increasing numbers of gaussians until little improvment is seen or max_k is reached.
    # Note: the algorithm must test on k + 1 to determine if k is optimal so function will test
    # max_k + 1 before timing out.
    for k in range(1, max_k + 2):
        params, log_likelihood = em_auto(data, k, num_guesses, num_iters)

        print(f"p-value for improvment for (k={k}) modes: {1 - stats.chi2.cdf(log_likelihood - prev_likelihood,2)}")

        # Use log likelihood test to determine whether improvements from
        # increasing k are statistically significant.
        if 1 - stats.chi2.cdf(log_likelihood - prev_likelihood, 2) > significance:
            print(f"Optimal model found with {k - 1} gaussians:")
            print(f"Optimal parameters are: {prev_params}")
            return prev_params, prev_likelihood
        
        prev_params = params
        prev_likelihood = log_likelihood

    raise ValueError(f"Optimal number of movement modes not found within {max_k} for given parameters.")

def gauss_pdf(x:float, mean:float, sd:float):
    # pdf for gaussian distribution.
    return (1 / np.sqrt(2 * np.pi * sd**2)) * np.exp(-(x - mean)**2 / (2 * sd**2))
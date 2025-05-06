import numpy as np
from scipy.stats import spearmanr
from scipy.spatial.distance import cdist, pdist
import matplotlib.pyplot as plt

def construct_RDM(data, n_target, method = "euclidean"):
    '''
    Input:
        data: n x m matrix, where n is the number of target and m is the number of features
        n_target: the number of target
        method: the method to calculate the distance matrix
            euclidean: Euclidean distance
            cityblock: Manhattan distance
            spearman: Spearman correlation
    Usage:
        construct_RDM(data, n_target, method = "euclidean")
    '''
    import numpy as np

    # check if the method is supported
    method = method.lower()
    if method not in ["euclidean", "cityblock", "spearman", "cosine"]:
        raise ValueError(f"Unsupported method: {method}. Supported methods are: euclidean, cityblock, spearman, cosine.")

    # unify the data format
    # Convert input to 2D numpy array
    data = np.asarray(data)
    if data.ndim == 1:
        data = data.reshape(-1, 1)  # make it (n_samples, 1) if it's a flat vector

    # Ensure shape is (n_target, features)
    if data.shape[0] == n_target:
        pass
    elif data.shape[1] == n_target:
        data = data.T
    else:
        raise ValueError(
            f'The input data does not have {n_target} observations. '
            f'It has {data.shape[0]} rows and {data.shape[1]} columns.'
        )

    if method == "spearman":
        corr_matrix, _ = spearmanr(data, axis = 1, nan_policy='omit')
        rdm = 1 - corr_matrix
    elif method == "cityblock":
        rdm = cdist(data, data, metric='cityblock')
    elif method == "cosine":
        rdm = cdist(data, data, metric='cosine')
    elif method == "euclidean":
        rdm = cdist(data, data, metric='euclidean')
    else:
        raise ValueError(f"Unsupported method: {method}")

    return rdm

def convert_RDM_to_vector(rdm):
    '''
    Convert a square RDM to a vector by removing the upper triangle.
    Input:
        rdm: n x n matrix
    Output:
        rdm_vector: n * (n - 1) / 2 vector
    '''
    # remove the upper triangle
    ind = np.tril_indices(rdm.shape[0], k=-1)
    rdm_vector = rdm[ind]
    
    return rdm_vector

def do_RSA(matrix1, matrix2, n_permutations=1000, random_state=None):
    """
    Perform Mantel permutations to calculate Spearman correlations.

    Parameters:
    -----------
    matrix1 : np.ndarray
        First distance matrix (square, symmetric).
    matrix2 : np.ndarray
        Second distance matrix (square, symmetric, same size as matrix1).
    n_permutations : int
        Number of permutations.
    random_state : int or None
        Random seed for reproducibility.

    Returns:
    --------
    permuted_correlations : np.ndarray
        Array of permuted Spearman correlation values.
    observed_correlation : float
        Observed Spearman correlation between original matrices.
    p_value : float
        P-value representing significance of the observed correlation.
    """
    if random_state is not None:
        np.random.seed(random_state)

    assert matrix1.shape == matrix2.shape, "Matrices must have the same dimensions"
    assert matrix1.shape[0] == matrix1.shape[1], "Matrices must be square"

    # Get the upper triangular indices
    triu_indices = np.triu_indices_from(matrix1, k=1)

    # Compute the observed correlation
    vec1 = matrix1[triu_indices]
    vec2 = matrix2[triu_indices]
    observed_correlation, _ = spearmanr(vec1, vec2)

    # Perform permutations
    permuted_correlations = np.zeros(n_permutations)
    n = matrix1.shape[0]

    for i in range(n_permutations):
        perm_indices = np.random.permutation(n)
        permuted_matrix2 = matrix2[perm_indices, :][:, perm_indices]
        perm_vec2 = permuted_matrix2[triu_indices]
        permuted_correlations[i], _ = spearmanr(vec1, perm_vec2)

    # Calculate p-value
    p_value = (np.sum(permuted_correlations >= observed_correlation) + 1) / (n_permutations + 1)

    # draw the histogram
    permutation_histogram(observed_correlation, permuted_correlations)
    
    return permuted_correlations, observed_correlation, p_value

def permutation_histogram(r, perm_r):
    '''
    Plot the histogram of permutation results on a created figure.
    '''
    fig, ax = plt.subplots(figsize=(8, 6))
    ax.hist(perm_r, bins=50, color='gray')
    ax.axvline(r, color='red', alpha=0.5)
    ax.text(r-0.01, 5, f'Observed r = {r:.2}', color='red', fontsize=16)
    ax.set_xlabel('Permutation r', fontsize=20)
    ax.set_ylabel('Frequency', fontsize=20)
    ax.tick_params(axis='both', labelsize=18)
    # ax.set_title('Permutation distribution', fontsize=22)
    plt.show()

def maximal_permutation_test(data, iv_single, iv_multiplecomp, n_perm = 1000):
    '''
    This fuction is used to address multiple comparison, \
        which provides an alternative of Bonferroni correction.
    
    - data: For IS-RSA, each row is a subject, while each column is a variable. \
        For example, if you have 20 subjects and 5 variables, the shape of data is (20, 5).
    - iv_single: the independent variable that will be shuffled and compare across iv_multiplecomp
    - iv_multiplecomp: the independent variable that are inter-related and elicit the multiple comparison problem
    - n_perm: number of permutation
    '''

    # construct the RDMs
    # convert the data into array
    ivSarray = data[iv_single].values.reshape(-1, 1)
    rdmS = construct_RDM(ivSarray, data.shape[0], method = "cityblock")

    # remove the upper triangle
    ind = np.tril_indices(rdmS.shape[0], k=-1)
    rdmS_f = rdmS[ind]

    # observed_r: dictionary to store the observed correlation
    observed_r = {}
    for ivM in iv_multiplecomp:
        # Construct the RDM for the independent variable component ivM.
        ivM_array = data[ivM].values.reshape(-1, 1)
        rdmM = construct_RDM(ivM_array, data.shape[0], method="cityblock")
        rdmM_f = rdmM[ind]
        
        # Compute the observed correlation between rdmS_f and rdmM_f.
        r, _ = spearmanr(rdmS_f, rdmM_f)
        observed_r[ivM] = r

    perm_r = np.zeros(n_perm)    
    for iperm in range(n_perm):
        # define the max r
        max_r_null = -np.inf

        # shuffle the data
        rdmS_shuffled = np.random.permutation(rdmS_f)

        for ivM in iv_multiplecomp:
            # construct the RDMs
            ivMarray = data[ivM].values.reshape(-1, 1)
            rdmM = construct_RDM(ivMarray, data.shape[0], method = "cityblock")
            rdmM_f = rdmM[ind]

            # calculate the psudo correlation
            r, _ = spearmanr(rdmS_shuffled, rdmM_f)

            # update the max r
            if r > max_r_null:
                max_r_null = r
            
        perm_r[iperm] = max_r_null
            
    # calculate the p-value
    perm_p = float(np.sum(perm_r > observed_r[ivM]) / n_perm)
    print(f"p = {np.sum(perm_r > observed_r[ivM])} / {n_perm}")

    return [perm_r, perm_p, observed_r]


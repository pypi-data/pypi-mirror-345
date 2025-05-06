import numpy as np
from tqdm import tqdm
from sklearn.decomposition import PCA


def make_r(data, scale_method):
    n, l, c = data.shape
    if scale_method=='y1':
        scale = data[:,0,:].reshape(n, 1, c)
    elif scale_method=='ymax':
        scale = np.max(np.abs(data), axis=1).reshape(n, 1, c)
    elif scale_method == 'noscale':
        scale = np.ones((n,1,c))
    r = data/ scale # shape (n, l, c)

    return r


def make_alpha(data) :
    means = np.mean(data, axis=0)
    variances = np.std(data, axis=0)
    alpha = means**2 / variances
    return alpha

# SNN matching
def make_rs_index(data, k):
    n, l, c = data.shape
    index_array = np.arange(n)
    rs_index = np.empty((n, k), dtype=int)

    # inv_cov_ = inv_cov(data)
    for i in tqdm(range(n), desc="Generating mixup indices"):
        x = data[i].reshape(1, l, c)
        xmat = data[np.arange(n) != i]
        prob = snn_proba(x, xmat, None)
        if np.any(np.isnan(prob)):  
            raise ValueError("probability contains NaN values.")
        
        del_arr = index_array[np.arange(n) != i]
        new_indices = np.random.choice(del_arr, size=k, replace=True, p=prob)
        rs_index[i] = new_indices

    return rs_index


####################################################################
# Mahalanobis Distance
def mahala_dist(x, data, inv_cov_matrix, normalize=False):
    x = x.reshape(1, -1)
    data = data.reshape(len(data), -1)

    mahalanobis_distances = []
    # Compute Mahalanobis distance for each sample in data
    for sample in data:
        diff = sample - x  # Compute the difference vector
        mahalanobis_distance = np.sqrt(diff @ inv_cov_matrix @ diff.T)  # Mahalanobis distance
        mahalanobis_distances.append(mahalanobis_distance[0,0])

    return np.array(mahalanobis_distances)

def inv_cov(data):
    data = data.reshape(len(data), -1)
    cov_matrix = np.cov(data, rowvar=False)  # Covariance matrix
    inv_cov_matrix = np.linalg.pinv(cov_matrix)  # Pseudo-inverse for stability

    return inv_cov_matrix

# random matching
def make_rs_index_random(data, k):
    n, l, c = data.shape
    index_array = np.arange(n)
    rs_index = np.empty((n, k), dtype=int)

    for i in tqdm(range(n), desc="Generating mixup indices"):
        del_arr = index_array[np.arange(n) != i]
        rs_index[i] = np.random.choice(del_arr, k, replace=True)
    return rs_index

def find_NN_index(dataframe, value, inv_cov_r):
    dist = np.linalg.norm(dataframe - value, ord='fro', axis=(1, 2))
    # dist = mahala_dist(value, dataframe, inv_cov_r)
    nn_index = np.argmin(dist)
    return nn_index

def make_rs_index_NN(data, r,  k):
    n, l, c = data.shape
    index_array = np.arange(n)
    rs_index = np.empty((n, k), dtype=int)

    # inv_cov_x = inv_cov(data)
    # inv_cov_r = inv_cov(r)
    for i in tqdm(range(n), desc="Generating mixup indices"):
        mask = np.arange(n) != i
        xmat = data[mask]                                                # shape (n-1, 20, c)
        nn_index = find_NN_index(xmat, data[i].reshape(1,l,c), None)

        del_arr = index_array[mask]
        rs_index[i] = np.full(k, del_arr[nn_index])
    return rs_index
####################################################################


####################################################################
def pca_decomp(data, center, n_comp=10):
    """
    Apply PCA to each channel (3rd dim) of input data of shape (n, l, c),
    and return PCA scores of shape (n, n_components, c).
    """
    n, l, c = data.shape
    n_comp = min(n_comp, l, n)
    scores_all = []

    for i in range(c):
        data_c = data[:, :, i]  # shape: (n, l)

        # Centering
        if center == 'sample_wise':
            sample_means = np.mean(data_c, axis=1, keepdims=True)  # shape: (n, 1)
            data_c_centered = data_c - sample_means

        elif center == 'feature_wise':
            feature_means = np.mean(data_c, axis=0, keepdims=True)  # shape: (1, l)
            data_c_centered = data_c - feature_means

        elif center == 'double':
            sample_means = np.mean(data_c, axis=1, keepdims=True)
            data_c_centered = data_c - sample_means
            feature_means = np.mean(data_c_centered, axis=0, keepdims=True)
            data_c_centered = data_c_centered - feature_means

        else:
            data_c_centered = data_c  # no centering

        # PCA
        U, S, Vt = np.linalg.svd(data_c_centered, full_matrices=False)
        principal_components = Vt.T[:, :n_comp]  # shape: (l, n_comp)
        scores = data_c_centered @ principal_components  # shape: (n, n_comp)
        scores_all.append(scores)

    scores_all = np.stack(scores_all, axis=-1)  # shape: (n, n_components, c)
    return scores_all



####################################################################


# calculate probabilities for SNN matching
def snn_proba(x, xmat, inv_cov_, temp=1.0):
    """
    Computes a probability distribution based on the Euclidean distances between a sample and a matrix of samples.

    Parameters:
    ----------
    x : np.ndarray
        A single sample with shape `(l, c)`.
    xmat : np.ndarray
        A matrix of samples with shape `(n-1, l, c)`.
    temp : float, optional
        Temperature parameter to control the sharpness of the probability distribution.
        Lower values make the distribution sharper.
        Default is 1.0.

    Returns:
    -------
    np.ndarray
        A 1D array of probabilities with length `n-1`.
    
    """
    # Flatten x and xmat to 1D vectors per sample
    
    dist = np.linalg.norm(xmat - x, ord='fro', axis=(1, 2))
    # dist = mahala_dist(x, xmat, inv_cov_)

    # use log sum exp trick
    min = np.min(dist)
    denom = np.log(sum(np.exp(-(dist-min)/temp)))-min/temp
    num = -dist/temp
    prob = np.exp(num-denom)

    return prob


# rstar matrix in a way that ensures the elements follow 12341234 ordering rather than 11223344 ordering.
def r_mixup(data, k, centering, scale_method, test_method) :
    """
    make rstar matrix
    """
    # assume data in 3 dim (n_samples, length, channels)
    n_comp = 20
    n, l, c = data.shape
    r = make_r(data, scale_method)

    if scale_method=='y1':
        if test_method == 'NN':
            scores = pca_decomp(data, center = centering, n_comp=n_comp)
            rs_index = make_rs_index_NN(scores, r, k)
        elif test_method == 'random':
            scores = pca_decomp(data, center = centering, n_comp=n_comp)
            rs_index = make_rs_index_random(scores, k)
        else:
            scores = pca_decomp(data, center = centering, n_comp=n_comp)
            rs_index = make_rs_index(scores, k)
    elif scale_method=='ymax':
        scores = pca_decomp(data, center = centering, n_comp=n_comp)
        rs_index = make_rs_index(scores, k)
    elif scale_method == 'noscale':
        scores = pca_decomp(data, center = centering, n_comp=n_comp)
        rs_index = make_rs_index(scores, k) 

    # scale factor
    if scale_method == 'y1':
        sf_i = data[:,:1,:]                                       # shape (n, 1, c)
    elif scale_method == 'ymax':                 
        sf_i = np.max(np.abs(data), axis=1)[:,np.newaxis,:]       # shape (n, 1, c)
    elif scale_method == 'noscale':
        sf_i = None
    
    if scale_method == 'y1':
        rmixup = []
        sf_mixup = []
        for j in range(k):
            rs = r[rs_index[:,j]]
            sf_s = sf_i[rs_index[:,j]]
            lamb = np.random.beta(a=0.5, b=0.5, size=(n,1,1))
            binom_mask = np.random.binomial(1, lamb, size=(n, 1, 1))
            sf_current = np.where(binom_mask == 1, sf_i, sf_s)
            rmixup.append(lamb*r + (1-lamb)*rs)
            sf_mixup.append(sf_current)
        rmixup_matrix = np.vstack(rmixup) # shape (n*k, l, c)
        sf_mixup_matrix = np.vstack(sf_mixup) # shape (n*k, 1, c)

    elif scale_method == 'ymax':
        rmixup = []
        sf_mixup = []
        for j in range(k):
            rs = r[rs_index[:,j]]                                 # shape (n, l, c)
            sf_s = sf_i[rs_index[:,j]]                            # shape (n, 1, c)
            lamb = np.random.beta(a=0.5, b=0.5, size=(n,1,1))
            rmixup.append(lamb*r + (1-lamb)*rs)
            sf_mixup.append(lamb*sf_i + (1-lamb)*sf_s)
        rmixup_matrix = np.vstack(rmixup)                         # shape (n*k, l, c)
        sf_mixup_matrix = np.vstack(sf_mixup)                     # shape (n*k, 1, c)

    elif scale_method == 'noscale':
        rmixup = []
        for j in range(k):
            rs = r[rs_index[:,j]]                                 # shape (n, l, c)               
            lamb = np.random.beta(a=0.5, b=0.5, size=(n,1,1))
            rmixup.append(lamb*r + (1-lamb)*rs)
        rmixup_matrix = np.vstack(rmixup)                         # shape (n*k, l, c)
        sf_mixup_matrix = None


    return rmixup_matrix, sf_mixup_matrix



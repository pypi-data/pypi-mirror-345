import numpy as np
import pandas as pd
from sklearn.mixture import GaussianMixture
from sklearn.linear_model import LinearRegression 
from sklearn.tree import DecisionTreeRegressor
from scipy.stats import norm
from DSTS.mixup import make_r


def gmm_draw_y1(data, rstar, n_comp, sf_mixup, sort) :
    sf_mixup = sf_mixup.squeeze() # shape (n*k, c)
    n, l, c = rstar.shape
    sf = data[:, 0, :]  # shape (n, c)

    sf_list = []
    for i in range(c):
        gmm = GaussianMixture(n_components=n_comp)
        gmm.fit(sf[:,i])
        sf_star, _ = gmm.sample(rstar.shape[0])
        sf_list.append(sf_star)

    sf_matrix = np.column_stack(sf_list) # shape (n*k, c)
    if sort:
        sf_matrix = np.sort(sf_matrix, axis=0)
        if c>1:
            for i in range(c):
                indices = np.argsort(sf_mixup[:,i])
                sf_matrix[:,i] = sf_matrix[indices,i]
        else:
            indices = np.argsort(sf_mixup)
            sf_matrix[:,i] = sf_matrix[indices,0]
    return sf_matrix


def gmm_draw_ymax(data, rstar, n_comp, sf_mixup, sort):
    sf_mixup = sf_mixup.squeeze() # shape (n*k, c)
    n, l, c = rstar.shape 
    sf = np.max(np.abs(data), axis=1)  # shape (n, c)

    sf_list = []
    for i in range(c):
        gmm = GaussianMixture(n_components=n_comp)
        gmm.fit(sf[:,i])
        sf_star, _ = gmm.sample(n)
        sf_list.append(sf_star)

    sf_matrix = np.column_stack(sf_list) # shape (n*k, c)
    if sort:
        sf_matrix = np.sort(sf_matrix, axis=0)
        if c>1:
            for i in range(c):
                indices = np.argsort(sf_mixup[:,i])
                sf_matrix[:,i] = sf_matrix[indices,i]
        else:
            indices = np.argsort(sf_mixup)
            sf_matrix[:,i] = sf_matrix[indices,0]
    return sf_matrix


def dt_draw_y1(data, rstar, sf_mixup, sort):
    sf_mixup = sf_mixup.squeeze() # shape (n*k, c)
    n, l, c = rstar.shape  # shape (n*k, l, c)
    r = make_r(data, 'y1') # shape (n, l, c)
    sf = data[:, 0, :]  # shape (n, c)
    
    sf_list = []
    for i in range(c):
        X_train = r[:, 1:3, i]  # shape (n, 2)
        y_train = sf[:, i]  # shape (n,)
        dt = DecisionTreeRegressor().fit(X_train, y_train)
    
        X_test = rstar[:, 1:3, i]  # shape (n*k, 2)
        y_test = dt.predict(X_test)  # shape (n*k,)
        sf_list.append(y_test)
    
    sf_matrix = np.column_stack(sf_list) # shape (n*k, c)
    
    if sort:
        sf_matrix = np.sort(sf_matrix, axis=0)
        if c>1:
            for i in range(c):
                indices = np.argsort(sf_mixup[:,i])
                sf_matrix[:,i] = sf_matrix[indices,i]
        else:
            indices = np.argsort(sf_mixup)
            sf_matrix[:,i] = sf_matrix[indices,0]
    return sf_matrix

def dt_draw_ymax(data, rstar, sf_mixup, sort):  
    sf_mixup = sf_mixup.squeeze() # shape (n*k, c)
    n, l, c = rstar.shape # shape (n*k, l, c)
    r = make_r(data, 'ymax')  # shape (n, l, c)
    sf = np.max(np.abs(data), axis=1)  # shape (n, c)
    
    sf_list = []
    for i in range(c):
        X_train = r[:, 1:3, i]  # shape (n, 2)
        y_train = sf[:, i]  # shape (n,)
        dt = DecisionTreeRegressor().fit(X_train, y_train)
    
        X_test = rstar[:, 1:3, i]  # shape (n*k, 2)
        y_test = dt.predict(X_test)  # shape (n*k,)
        sf_list.append(y_test)
    
    sf_matrix = np.column_stack(sf_list) # shape (n*k, c)
    
    if sort:
        sf_matrix = np.sort(sf_matrix, axis=0)
        if c>1:
            for i in range(c):
                indices = np.argsort(sf_mixup[:,i])
                sf_matrix[:,i] = sf_matrix[indices,i]
        else:
            indices = np.argsort(sf_mixup)
            sf_matrix[:,i] = sf_matrix[indices,0]
    return sf_matrix


# def mixup_draw_ymax(data, rstar, rs_index, k):  
#     n, l, c = rstar.shape # shape (n*k, l, c)
#     r = make_r(data, 'ymax')  # shape (n, l, c)
#     sf = np.max(np.abs(data), axis=1)  # shape (n, c)
    
#     sf_list = []
#     for i in range(k):

#         np.random.choice(del_arr, k, replace=True)

    
#     sf_matrix = np.column_stack(sf_list) # shape (n*k, c)
    
#     return sf_matrix

# Linear regression method
def lr_draw_y1(data, rstar, sort) :
    r = make_r(data)
    size = len(data)
    y = data[:,0]
    lr = LinearRegression().fit(r[:,:2], data[:,0])
    y_hat = lr.predict(r[:,:2])
    sig_hat = np.sqrt((y-y_hat)@(y-y_hat)/(size-2))
    y1 = np.random.normal(loc = lr.predict(rstar[:,:2]), scale = sig_hat, size = len(rstar))
    if sort:
        y1 = y1.squeeze()
        y1 = np.sort(y1)

    return np.squeeze(y1)


# conditional GMM method
def init_pi(n_comp):
    arr = np.random.rand(n_comp)
    sum = np.sum(arr)

    return arr/sum


def fit_GMM(y1, r, n_comp):
    """
    Fit GMM using EM
    """
    size = len(y1)
    # initialize parameters
    b0 = np.random.rand(n_comp)*10
    b1 = np.random.rand(n_comp)*10
    s2 = np.random.rand(1)*10
    pi = init_pi(n_comp)
    z = np.zeros((size, n_comp))

    while (True):
        b00 = b0
        b10 = b1
        s20 = s2
        pi0 = pi
        diff = 0

        # E-step
        # z
        for i in range(size):
            for k in range(n_comp):
                z[i,k] = pi[k]*norm.pdf(y1[i], b0[k]+b1[k]*r[i,0], np.sqrt(s2)).item()/np.sum(np.fromiter((pi[j]*norm.pdf(y1[i], b0[j]+b1[j]*r[i,0], np.sqrt(s2)).item() for j in range(n_comp)), dtype=float))

        # M-step
        # pi
        pi = np.sum(z, axis=0)/np.sum(z)
        diff+=np.sum(np.abs(pi0-pi))

        # b0
        for k in range(n_comp):
            b0[k] = z[:,k]@(y1-b1[k]*r[:,0])/np.sum(z[:,k])
        diff+=np.sum(np.abs(b00-b0))

        # b1
        for k in range(n_comp):
            b1[k] = z[:,k]@(r[:,0]*(y1-b0[k]))/(z[:,k]@(r[:,0]**2))
        diff+=np.sum(np.abs(b10-b1))

        # sigma
        s2 = np.sum(np.fromiter(((y1-b0[k]-b1[k]*r[:,0])**2@z[:,k]/np.sum(z[:,k]) for k in range(n_comp)), dtype=float))
        diff+=np.sum(np.abs(s20-s2))

        if (diff<1e-5): break
    
    return b0, b1, s2, pi


def condGMM_draw_y1(data, rstar, n_comp, sort) :
    y1 = data[:,0]
    r = make_r(data)
    b0, b1, s2, pi = fit_GMM(y1, r, n_comp)
    z = np.argmax(np.random.multinomial(1, pi, size=len(rstar)), axis=1)
    mean = b0[z]+b1[z]*rstar[:,0]
    std = s2
    y1_hat = np.random.normal(mean, std, size=len(rstar))
    if sort:
        y1_hat = y1_hat.squeeze()
        y1_hat = np.sort(y1_hat)

    return y1_hat.squeeze()

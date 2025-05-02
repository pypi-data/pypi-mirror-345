# spatial_statistics/spatial_relationships.py

import numpy as np
from sklearn.neighbors import NearestNeighbors
from scipy.sparse import csr_matrix

def knn_weight_matrix(coordinates, k=4, row_standardized=False, return_sparse=True, symmetric=True):
    """
    Compute an optimized KNN-based spatial weight matrix.

    Parameters:
    - coordinates: array-like of shape (n_samples, 2), spatial points
    - k: number of nearest neighbors
    - row_standardized: if True, rows will be normalized to sum to 1
    - return_sparse: if True, returns scipy.sparse CSR matrix; else returns dense NumPy array
    - symmetric: if True, makes matrix symmetric (mutual neighbors)

    Returns:
    - W: spatial weight matrix (CSR or NumPy ndarray)
    """
    coords = np.asarray(coordinates)
    n = coords.shape[0]

    nbrs = NearestNeighbors(n_neighbors=k + 1).fit(coords)
    distances, indices = nbrs.kneighbors(coords)

    # Remove self-neighbor (assumed to be first)
    row_indices = np.repeat(np.arange(n), k)
    col_indices = indices[:, 1:(k+1)].reshape(-1)
    data = np.ones(len(row_indices))

    # Build sparse matrix
    W = csr_matrix((data, (row_indices, col_indices)), shape=(n, n))

    if symmetric:
        W = W.maximum(W.T)  # ensure symmetry: W[i,j] = W[j,i]

    if row_standardized:
        row_sums = np.array(W.sum(axis=1)).flatten()
        row_sums[row_sums == 0] = 1  # avoid division by zero
        inv_row_sums = 1.0 / row_sums
        W = W.multiply(inv_row_sums[:, np.newaxis])  # row-standardization

    if return_sparse:
        return W
    else:
        return W.toarray()

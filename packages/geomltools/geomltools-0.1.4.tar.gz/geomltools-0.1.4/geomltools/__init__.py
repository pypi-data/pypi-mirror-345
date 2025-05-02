"""
GeoML: A Python library for spatial machine learning and geospatial analysis.

This library provides tools for analyzing spatial data,
as well as implementing spatial machine learning algorithms.

Key Features:
- Spatial statistics (e.g., Moran's I, Spatial Variance Ratio)

"""

# Import key functions and classes
from .spatial_statistics.spatial_indices import morans_i, spatial_variance_ratio, permutation_test
from .spatial_statistics.spatial_relationships import knn_weight_matrix


# Optional: Define __all__ to control what gets imported with `from geoml import *`
__all__ = [
    'morans_i',
    'spatial_variance_ratio',
    'permutation_test',
    'knn_weight_matrix'
]


__version__ = "0.1.4" 
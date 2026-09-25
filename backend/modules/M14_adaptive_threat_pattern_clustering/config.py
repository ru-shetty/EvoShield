"""
Configuration for Module 14:
Adaptive Threat Pattern Clustering
"""

# Number of clusters
K = 5

# Feature vector dimension.
# Set to None if you want it to be automatically detected
# from the first incoming batch.
FEATURE_DIMENSION = None

# MiniBatchKMeans
BATCH_SIZE = 64
RANDOM_STATE = 42

# EWMA parameters
ALPHA = 0.1

# Drift detection threshold
K_SIGMA = 3.0

# PSI threshold
PSI_THRESHOLD = 0.2

# Number of batches used for baseline warmup
WARMUP_BATCHES = 5

# Recent feature vectors retained for retraining
RECENT_WINDOW_SIZE = 500

# Minimum variance to avoid division by zero
VARIANCE_EPSILON = 1e-8

# Minimum probability used in PSI calculation
PSI_EPSILON = 1e-6

# Maximum number of samples kept in memory for initial KMeans fitting
INITIAL_BUFFER_SIZE = 5000
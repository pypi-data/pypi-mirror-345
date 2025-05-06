import numpy as np

class k_fold:
  @staticmethod
  def split(X: np.ndarray, y: np.ndarray, *, k=5, perm: np.ndarray | None = None):
    """K-fold cross-validation generator. Yields `(X_train, y_train, X_val, y_val)` for each of the `k` folds."""
    n = X.shape[0]
    if perm is None:
      perm = np.random.permutation(n)
    n_test = n // k
    for i in range(k):
      I_val = perm[n_test*i:n_test*(i+1)]
      I_train = np.setdiff1d(perm, I_val)
      X_train, y_train = X[I_train], y[I_train]
      X_val, y_val = X[I_val], y[I_val]
      yield X_train, y_train, X_val, y_val

  @staticmethod
  def ith(X: np.ndarray, y: np.ndarray, i: int, *, k=5, perm: np.ndarray | None = None):
    """i-th fold of k-fold cross-validation. Returns `(X_train, y_train, X_val, y_val)`."""
    n = X.shape[0]
    if perm is None:
      perm = np.random.permutation(n)
    n_test = n // k
    I_val = perm[n_test*i:n_test*(i+1)]
    I_train = np.setdiff1d(perm, I_val)
    X_train, y_train = X[I_train], y[I_train]
    X_val, y_val = X[I_val], y[I_val]
    return X_train, y_train, X_val, y_val
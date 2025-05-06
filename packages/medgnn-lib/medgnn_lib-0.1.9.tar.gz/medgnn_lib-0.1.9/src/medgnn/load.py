import os
import numpy as np

DATA_PATH = os.path.abspath(os.path.join(__file__, os.pardir, os.pardir, os.pardir, os.pardir, 'data'))

def StandardScaler():
  from sklearn.preprocessing import StandardScaler
  return StandardScaler()

class load:
  @staticmethod
  def mat(name: str, data_path: str = DATA_PATH) -> tuple[np.ndarray, np.ndarray]:
    """Returns `(X, y)`, with `X :: [n, d]`, `y :: [n]`"""
    from scipy.io import loadmat
    data: dict = loadmat(os.path.join(data_path, name))
    X = data['X']
    y = data.get('Y')
    if y is None:
      y = data['y']
    y = y[:, 0]
    return X, y

  @staticmethod
  def allaml(name: str = 'ALLAML.mat', data_path: str = DATA_PATH):
    X_raw, y_raw = load.mat(name, data_path)
    X = StandardScaler().fit_transform(X_raw)
    y = y_raw-1 # {1, 2} -> {0, 1}
    return X, y
  
  @staticmethod
  def tox(name: str = 'TOX_171.mat', data_path: str = DATA_PATH):
    X_raw, y_raw = load.mat(name, data_path)
    X = StandardScaler().fit_transform(X_raw)
    y = y_raw-1 # {1, 2} -> {0, 1}
    return X, y
  
  @staticmethod
  def cll(name: str = 'CLL_SUB_111.mat', data_path: str = DATA_PATH):
    X_raw, y_raw = load.mat(name, data_path)
    X = StandardScaler().fit_transform(X_raw)
    y = y_raw-1 # {1, 2} -> {0, 1}
    return X, y

  @staticmethod
  def gli(name: str = 'GLI_85.mat', data_path: str = DATA_PATH):
    X_raw, y_raw = load.mat(name, data_path)
    X = StandardScaler().fit_transform(X_raw)
    y = y_raw-1 # {1, 2} -> {0, 1}
    return X, y

  @staticmethod
  def prostate(name: str = 'Prostate_GE.mat', data_path: str = DATA_PATH):
    X_raw, y_raw = load.mat(name, data_path)
    X = StandardScaler().fit_transform(X_raw)
    y = y_raw-1 # {1, 2} -> {0, 1}
    return X, y

  @staticmethod
  def smk(name: str = 'SMK_CAN_187.mat', data_path: str = DATA_PATH):
    X_raw, y_raw = load.mat(name, data_path)
    X = StandardScaler().fit_transform(X_raw)
    y = y_raw-1 # {1, 2} -> {0, 1}
    return X, y

  @staticmethod
  def tran(name: str = 'tran.mat', data_path: str = DATA_PATH):
    X_raw, y = load.mat(name, data_path)
    X = StandardScaler().fit_transform(X_raw)
    return X, y
  
  @staticmethod
  def oscc(name: str = 'oscc-ms.mat', data_path: str = DATA_PATH):
    X_raw, y = load.mat(name, data_path)
    X_raw[np.isnan(X_raw)] = -1
    X = StandardScaler().fit_transform(X_raw)
    return X, y
  
  @staticmethod
  def lipid_nafld(name: str = 'lipid-nafld.mat', data_path: str = DATA_PATH):
    X_raw, y = load.mat(name, data_path)
    X = StandardScaler().fit_transform(X_raw)
    return X, y
  
  @staticmethod
  def binary_datasets(data_path: str = DATA_PATH):
    return {
      'allaml': lambda: load.allaml(data_path=data_path),
      'gli': lambda: load.gli(data_path=data_path),
      'prostate': lambda: load.prostate(data_path=data_path),
      'smk': lambda: load.smk(data_path=data_path),
      'tran': lambda: load.tran(data_path=data_path),
      'oscc': lambda: load.oscc(data_path=data_path),
    }

  @staticmethod
  def datasets(data_path: str = DATA_PATH):
    return load.binary_datasets(data_path) | {
      'tox': lambda: load.tox(data_path=data_path),
      'cll': lambda: load.cll(data_path=data_path),
    }
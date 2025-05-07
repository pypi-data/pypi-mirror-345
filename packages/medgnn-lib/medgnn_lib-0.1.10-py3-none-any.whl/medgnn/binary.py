import numpy as np
from sklearn.metrics import precision_score, recall_score, roc_auc_score, accuracy_score, f1_score, roc_curve

class binary:
  @staticmethod
  def metrics(probs: np.ndarray, labels: np.ndarray, *, threshold=0.5):
    preds = (probs > threshold).astype(int)
    return {
      'accuracy': accuracy_score(labels, preds),
      'AUC': float(roc_auc_score(labels, preds)),
      'precision': precision_score(labels, preds, zero_division=0),
      'recall': recall_score(labels, preds, zero_division=0),
      'f1': f1_score(labels, preds, zero_division=0),
      'positives': float(preds.mean()), # proportion of positive predictions
    }
  
  @staticmethod
  def plot_roc(probs: np.ndarray, labels: np.ndarray, ax=None):
    import matplotlib.pyplot as plt
    ax = ax or plt.gca()
    fpr, tpr, _ = roc_curve(labels, probs)
    ax.plot(fpr, tpr, color='blue', label='ROC curve')
    ax.plot([0, 1], [0, 1], color='red', linestyle='--')
    ax.set_xlabel('False Positive Rate')
    ax.set_ylabel('True Positive Rate')
    ax.set_title('Receiver Operating Characteristic')
    ax.legend(loc='lower right')
    return ax
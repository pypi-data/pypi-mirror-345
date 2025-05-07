from sklearn.linear_model import RidgeClassifierCV
from sklearn.utils.extmath import softmax
import numpy as np


class RidgeClassifierCVFix(RidgeClassifierCV):

    def predict_proba(self, X):
        d = self.decision_function(X)
        if len(d.shape) == 1:
            d = np.c_[-d, d]
        return softmax(d)

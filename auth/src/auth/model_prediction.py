import os
import matplotlib.pyplot as plt
import numpy as np
import pickle
import sklearn

def model_prediction(payload):
    this_fv = np.frombuffer(payload, dtype=np.uint16)
    # fm_dir = "data/feature_matrices/"  # where to save the features matrices
    filename = "auth/src/auth/model.pickle"
    model = pickle.load(open(filename, "rb"))
    mat = np.zeros((2, len(this_fv)))
    mat[0] = this_fv
    prediction = model.predict(mat)
    return prediction[0]
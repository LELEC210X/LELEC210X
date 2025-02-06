import os
import pickle
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from typing import Any, Optional, Dict, List
from abc import ABC, abstractmethod
from dataclasses import dataclass
from sklearn.tree import DecisionTreeClassifier
from sklearn.model_selection import StratifiedKFold, train_test_split
from sklearn.base import BaseEstimator


####################################################################################################
# Abstract Classes

class AbstractModelWrapper(ABC):
    """Abstract base class for a model wrapper."""

    def __init__(self, model: BaseEstimator, classes: List[str]):
        self.model = model
        self.classes = classes

    @abstractmethod
    def predict(self, X: np.ndarray) -> np.ndarray:
        """Predict the probabilities of the classes."""
        pass

    @abstractmethod
    def predict_hist(self, X: List[np.ndarray]) -> np.ndarray:
        """Predict the probabilities of the classes for the whole history."""
        pass


####################################################################################################
# Model Wrapper Implementation (Example)

class DecisionTreeWrapper(AbstractModelWrapper):
    """Decision tree model wrapper that supports pickling."""

    def __init__(self, model: DecisionTreeClassifier, classes: List[str]):
        super().__init__(model, classes)

    def predict(self, X: np.ndarray) -> np.ndarray:
        """Predict class probabilities."""
        return self.model.predict_proba(X)

    def predict_hist(self, X: List[np.ndarray]) -> np.ndarray:
        """Predict class probabilities over a sequence and return the average."""
        proba_list = [self.model.predict_proba(x) for x in X]
        return np.mean(proba_list, axis=0)

    def __getstate__(self):
        """Ensure picklability by storing only necessary attributes."""
        return {
            "model_state": self.model.__getstate__(),
            "classes": self.classes
        }

    def __setstate__(self, state):
        """Restore pickled object."""
        self.model = DecisionTreeClassifier()  # Create a new instance
        self.model.__setstate__(state["model_state"])  # Restore model state
        self.classes = state["classes"]


# USER CODE HERE





####################################################################################################
# Model Serialization Format

@dataclass
class ModelPickleFormat:
    """Data structure for storing model metadata and parameters."""
    model_state: Dict[str, Any]  # Pickled model state
    classes: List[str]           # List of class labels
    mel_len: int                 # Mel vector length
    mel_num: int                 # Number of mel vectors
    mel_flat: bool               # Whether mel vectors are flattened
    needs_hist: bool             # Whether model needs history
    concat_hist: bool            # Whether history is concatenated
    num_hist: int                # Number of history elements

    def to_dict(self) -> Dict[str, Any]:
        """Convert the model format to a dictionary."""
        return self.__dict__

    @staticmethod
    def from_dict(model_dict: Dict[str, Any]) -> Optional["ModelPickleFormat"]:
        """Convert a dictionary back into a ModelPickleFormat object."""
        required_keys = [
            "model_state", "classes", "mel_len", "mel_num", 
            "mel_flat", "needs_hist", "concat_hist", "num_hist"
        ]
        if not all(key in model_dict for key in required_keys):
            return None
        return ModelPickleFormat(**model_dict)


####################################################################################################
# Model Persistence Functions

def save_model(wrapper: DecisionTreeWrapper, model_format: ModelPickleFormat, path: str):
    """Save the model and its metadata to a pickle file."""
    model_format_dict = model_format.to_dict()
    model_format_dict["model_state"] = wrapper.__getstate__()

    with open(path, "wb") as file:
        pickle.dump(model_format_dict, file)


def load_model(path: str) -> Optional[DecisionTreeWrapper]:
    """Load the model from a pickle file."""
    with open(path, "rb") as file:
        model_dict = pickle.load(file)

    model_format = ModelPickleFormat.from_dict(model_dict)
    if model_format is None:
        return None

    # Restore the model
    restored_model = DecisionTreeWrapper(DecisionTreeClassifier(), model_format.classes)
    restored_model.__setstate__(model_dict["model_state"])

    return restored_model


####################################################################################################
# Example Usage

if __name__ == "__main__":
    # Define model and class labels
    model_to_use = DecisionTreeClassifier(max_depth=5, min_samples_split=2)
    classes = ["class1", "class2", "class3"]

    # Generate sample training data
    X = np.random.rand(40, 400)
    y = np.random.choice(classes, 40)

    # Modify data for class1
    X[y == "class1"] = np.ones(400) / 2

    # Train the model
    model_to_use.fit(X, y)

    # Wrap the trained model
    model_wrapper = DecisionTreeWrapper(model_to_use, classes)

    # Define model metadata
    model_format = ModelPickleFormat(
        model_state=model_wrapper.__getstate__(),
        classes=classes,
        mel_len=20,
        mel_num=20,
        mel_flat=True,
        needs_hist=True,
        concat_hist=False,
        num_hist=3
    )

    # Save the model
    save_model(model_wrapper, model_format, "model.pickle")

    # Load the model
    loaded_model = load_model("model.pickle")

    # Test the loaded model
    if loaded_model:
        X_test = np.random.rand(3, 400)
        print(loaded_model.predict(X_test[0].reshape(1, -1)))
        print(loaded_model.predict_hist([X_test[i].reshape(1, -1) for i in range(len(X_test))]))
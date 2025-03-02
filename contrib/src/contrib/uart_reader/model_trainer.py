import os
import pickle
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, Dict, List, Optional

import numpy as np
from sklearn.base import BaseEstimator
from sklearn.tree import DecisionTreeClassifier

####################################################################################################
# Abstract Classes


class AbstractModelWrapper(ABC):
    """Abstract base class for a model wrapper."""

    model: BaseEstimator
    classes: List[str]

    def __init__(self, model: BaseEstimator, classes: List[str]):
        self.model = model
        self.classes = classes

    def __getstate__(self):
        """Return the pickled state of the object."""
        return {"model_state": self.model.__getstate__(), "classes": self.classes}

    def __setstate__(self, state):
        """Set the state of the object from the pickled state."""
        self.model.__setstate__(state["model_state"])
        self.classes = state["classes"]

    # To be implemented by subclasses
    @abstractmethod
    def predict(self, X: np.ndarray[np.ndarray]) -> np.ndarray:
        """
        Predict the probabilities of the classes.
        The input X is a 2D array of shape (n_samples, n_features).
        """
        pass

    @abstractmethod
    def predict_hist(self, X: List[np.ndarray[np.ndarray]]) -> np.ndarray:
        """
        Predict the probabilities of the classes for the whole history.
        The input X is a list of 2D arrays of shape (n_samples, n_features).
        """
        pass


####################################################################################################
# Model Wrapper Implementation (Example)


class DecisionTreeWrapper(AbstractModelWrapper):
    """Decision tree model wrapper that supports pickling."""

    model: DecisionTreeClassifier
    classes: List[str]

    def __init__(self, model: DecisionTreeClassifier, classes: List[str]):
        super().__init__(model, classes)

    def __getstate__(self):
        return {"model": self.model, "classes": self.classes}

    def __setstate__(self, state):
        self.model = state["model"]
        self.classes = state["classes"]

    def predict(self, X: np.ndarray[np.ndarray]) -> np.ndarray:
        """Predict class probabilities."""
        return self.model.predict_proba(X)

    def predict_hist(self, X: List[np.ndarray[np.ndarray]]) -> np.ndarray:
        """Predict class probabilities over a sequence and return the average."""
        proba_list = [self.model.predict_proba(x) for x in X]
        return np.mean(proba_list, axis=0)


# USER CODE HERE


####################################################################################################
# Model Serialization Format


@dataclass
class ModelPickleFormat:
    """Data structure for storing model metadata and parameters."""

    model: AbstractModelWrapper  # Model wrapper object
    classes: List[str]  # List of class labels
    mel_len: int  # Mel vector length
    mel_num: int  # Number of mel vectors
    mel_flat: bool  # Whether mel vectors are flattened
    needs_hist: bool  # Whether model needs history
    concat_hist: bool  # Whether history is concatenated
    num_hist: int  # Number of history elements

    def to_dict(self) -> Dict[str, Any]:
        """Convert the model format to a dictionary."""
        return {
            "model": self.model,
            "classes": self.classes,
            "mel_len": self.mel_len,
            "mel_num": self.mel_num,
            "mel_flat": self.mel_flat,
            "needs_hist": self.needs_hist,
            "concat_hist": self.concat_hist,
            "num_hist": self.num_hist,
        }

    @staticmethod
    def from_dict(model_dict: Dict[str, Any]) -> Optional["ModelPickleFormat"]:
        """Convert a dictionary back into a ModelPickleFormat object."""
        if "model" not in model_dict:
            return None

        return ModelPickleFormat(
            model=model_dict["model"],
            classes=model_dict["classes"],
            mel_len=model_dict["mel_len"],
            mel_num=model_dict["mel_num"],
            mel_flat=model_dict["mel_flat"],
            needs_hist=model_dict["needs_hist"],
            concat_hist=model_dict["concat_hist"],
            num_hist=model_dict["num_hist"],
        )


####################################################################################################
# Model Persistence Functions


def save_model(model_format: ModelPickleFormat, path: str):
    """Save the model and its metadata to a pickle file."""
    model_dict = model_format.to_dict()
    with open(path, "wb") as file:
        pickle.dump(model_dict, file)


def load_model(path: str) -> Optional[ModelPickleFormat]:
    """Load the model and its metadata from a pickle file."""
    if not os.path.exists(path):
        return None

    with open(path, "rb") as file:
        model_dict = pickle.load(file)
        return ModelPickleFormat.from_dict(model_dict)

    return None


####################################################################################################
# Example Usage
# (Tip: Use tqdm and regularly backup your model to avoid losing progress if the training fails or gets interrupted)

ADC_MAX_VALUE = 2**16


def example():
    """Example usage of the model serialization functions."""
    # Define model and class labels
    model_to_use = DecisionTreeClassifier(max_depth=5, min_samples_split=2)
    classes = ["class1", "class2", "class3", "class4", "class5", "class6"]

    # Generate sample training data
    X = np.random.rand(40, 400) * ADC_MAX_VALUE
    y = np.random.choice(classes, 40)

    # Modify data for class1 for a bit of separation (since its random data)
    X[y == "class1"] = np.ones(400) * ADC_MAX_VALUE / 2

    # Train the model
    model_to_use.fit(X, y)

    # Wrap the trained model
    model_wrapper = DecisionTreeWrapper(model_to_use, classes)

    # Define model metadata
    model_format = ModelPickleFormat(
        model=model_wrapper,
        classes=classes,
        mel_len=20,
        mel_num=20,
        mel_flat=True,
        needs_hist=False,
        concat_hist=False,
        num_hist=0,
    )

    # Save the model
    file_origin = os.path.dirname(os.path.abspath(__file__))
    save_model(model_format, os.path.join(file_origin, "model.pickle"))

    # Load the model
    loaded_model = load_model(os.path.join(file_origin, "model.pickle"))
    if loaded_model is not None:
        print("Model loaded successfully!")
    else:
        print("Failed to load model!")

    # Predict using the loaded model
    X_test = np.random.rand(400) * ADC_MAX_VALUE
    X_test = X_test.reshape(1, -1)  # Reshape to 2D array for the model
    print(loaded_model.model.predict(X_test))

    # Predict using the loaded model with history
    X_hist = [(np.random.rand(400) * ADC_MAX_VALUE).reshape(1, -1) for _ in range(10)]
    print(loaded_model.model.predict_hist(X_hist))


# Run the Main Function (Example or user code)
def main():
    example()  # COMMENT THIS LINE TO RUN USER CODE

    # USER CODE HERE


# Run the function
if __name__ == "__main__":
    print(
        "Please run this through rye instead, using >> rye run model-trainer <<, else, the model will not be interpreted correctly on load."
    )
    main()

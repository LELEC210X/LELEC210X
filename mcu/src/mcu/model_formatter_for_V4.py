import os
import matplotlib.pyplot as plt
import numpy as np
import pickle
from sklearn.model_selection import StratifiedKFold, train_test_split
import pandas as pd
from sklearn.tree import DecisionTreeClassifier

from classification.datasets import Dataset
from classification.utils.audio_student import AudioUtil, Feature_vector_DS
from classification.utils.plots import (
    plot_decision_boundaries,
    plot_specgram,
    show_confusion_matrix,
)

max_str_length = 20
def index_to_augmentation(index, distorsion_to_add = ["noise"]):
    """
    Take a list of indexes and return the corresponding augmented feature matrix
    """
    aug_factor = len(distorsion_to_add)+1
    nb_sample = len(index)
    X_aug = np.zeros((aug_factor * nclass * nb_sample, featveclen))
    y_aug = np.zeros((aug_factor * nclass * nb_sample ), dtype=f"<U{max_str_length}")
    
    
    for s in range(aug_factor):
        if s == 0:
            myds.mod_data_aug([])
        if s != 0:
            myds.mod_data_aug([distorsion_to_add[s - 1]])
        count = 0
        for idx in index:
            for class_idx, classname in enumerate(classnames):
                featvec = myds[classname, idx]
                X_aug[s * nclass * nb_sample + class_idx * nb_sample + count, :] = featvec
                y_aug[s * nclass * nb_sample + class_idx * nb_sample + count] = classname
            count += 1
    
    return X_aug, y_aug


# decision method from a matrix of probabilities probs = np.zeros((n_win, len(classnames))) to a single class
# first method : naive : take the class with the highest probability in the matrix
def decision_naive(probs, classnames):
    index = np.argmax(probs) % len(classnames)
    return classnames[index]

# second method : majority vote : take the class with the highest number of votes
def decision_majority(probs, classnames):
    n_win = probs.shape[0]
    votes = np.argmax(probs, axis=1)
    count = np.bincount(votes)
    max_indices = np.where(count == count.max())[0]
    predicted_classes = [classnames[i] for i in max_indices]
    for prio_class in priority_order:
        if prio_class in predicted_classes:
            return prio_class

# third method : weighted majority vote : take the class with the highest sum of probabilities
def decision_weighted(probs, classnames):
    sum_probs = np.sum(probs, axis=0)
    return classnames[np.argmax(sum_probs)]


# fourth method : maximum likelihood : take the class with the product of the probabilities
def decision_maxlikelihood(probs, classnames):
    prod_probs = np.prod(probs, axis=0)
    return classnames[np.argmax(prod_probs)]

dataset = Dataset()
classnames = dataset.list_classes()
myds = Feature_vector_DS(dataset, Nft=512, nmel=20, duration=950, shift_pct=0.0)
nclass = len(classnames)
naudio = dataset.naudio
featveclen = len(myds["fire", 0])
priority_order = ["fire", "handsaw", "chainsaw", "helicopter", "birds"]

# [0] Create a dataset and augment it
indexes = np.arange(40)
X, y = index_to_augmentation(indexes, "time_shift")
X = X/np.linalg.norm(X, axis=1, keepdims=True)


# [1] Split the dataset into a training and a test set.
X_learn, X_test, y_learn, y_test = train_test_split(X, y, test_size=0.3, stratify=y, shuffle=True, random_state=55)


# [2] Model training and selection.

nfolds = 4
# max_depth = [5, 10, 20, 30, 40, 50, 60, 70, 80, 90, 100, 110, 120, 130, 140, 150]
max_depth = [5, 10, 20, 30]
# min_samples_split = [2,3,4,5,6,7,8,9,10]
min_samples_split = [2,3,4,5]


results = pd.DataFrame(columns=["max_depth","min_samples_split","decision_method","mean_macro_F1_score","std_macro_F1_score"])

# K fold cross validation
kf = StratifiedKFold(n_splits=nfolds, shuffle=True, random_state=55)

for depth in max_depth:
    for split in min_samples_split:
        model = DecisionTreeClassifier(max_depth=depth, min_samples_split=split)
        F1_scores = []
        for train_idx, test_idx in kf.split(X, y):
            X_train, y_train = X[train_idx], y[train_idx]
            X_test, y_test = X[test_idx], y[test_idx]
            model.fit(X_train, y_train)
            predictions = model.predict(X_test)
            confusion_matrix = np.zeros((len(classnames), len(classnames)))
            for i in range(len(classnames)):
                for j in range(len(classnames)):
                    confusion_matrix[i, j] = np.sum((y_test == classnames[i]) & (predictions == classnames[j]))
            F1_scores = []
            for i in range(len(classnames)):
                TP = confusion_matrix[i, i]
                FP = np.sum(confusion_matrix[:, i]) - TP
                FN = np.sum(confusion_matrix[i, :]) - TP
                precision = TP / (TP + FP)
                recall = TP / (TP + FN)
                F1 = 2 * precision * recall / (precision + recall)
                F1_scores.append(F1)
        mean_F1 = np.mean(F1_scores)
        std_F1 = np.std(F1_scores)
        results = results._append({"max_depth":depth, "min_samples_split":split, "mean_macro_F1_score":mean_F1, "std_macro_F1_score":std_F1}, ignore_index=True)
        
# print best hyperparameters and best F1 score
best_idx = results["mean_macro_F1_score"].idxmax()
best_depth = results.loc[best_idx, "max_depth"]
best_depth = int(best_depth)
best_split = results.loc[best_idx, "min_samples_split"]
best_split = int(best_split)
best_F1 = results.loc[best_idx, "mean_macro_F1_score"]
print("Best hyperparameters: max_depth = {}, min_samples_split = {}".format(best_depth, best_split))
print("Best F1 score: {}".format(best_F1))

#plot a heatmap of the F1 scores
results = results.pivot_table(index="max_depth", columns="min_samples_split", values="mean_macro_F1_score")
plt.figure()
plt.imshow(results, cmap='coolwarm')  # Change colormap here (e.g., 'viridis', 'plasma', 'cividis', 'coolwarm')
plt.xlabel("min_samples_split")
plt.ylabel("max_depth")
plt.xticks(np.arange(len(min_samples_split)), min_samples_split)
plt.yticks(np.arange(len(max_depth)), max_depth)
plt.title("Macro F1 score")
plt.savefig("hyperparameters_heatmap.pdf")


# [3] Train the model with the best hyperparameters.

model = DecisionTreeClassifier(max_depth=best_depth, min_samples_split=best_split)
model.fit(X_learn, y_learn)
            


# [4] Evaluate the model on the test set.
print(len(X_test))
predictions = model.predict(X_test)
confusion_matrix = np.zeros((len(classnames), len(classnames)))
for i in range(len(classnames)):
    for j in range(len(classnames)):
        confusion_matrix[i, j] = np.sum((y_test == classnames[i]) & (predictions == classnames[j]))
        
F1_scores = []
for i in range(len(classnames)):
    TP = confusion_matrix[i, i]
    FP = np.sum(confusion_matrix[:, i]) - TP
    FN = np.sum(confusion_matrix[i, :]) - TP
    precision = TP / (TP + FP)
    recall = TP / (TP + FN)
    F1 = 2 * precision * recall / (precision + recall)
    F1_scores.append(F1)
    
mean_F1 = np.mean(F1_scores)
print("F1 score on test set: {}".format(mean_F1))


plt.figure()
plt.imshow(confusion_matrix, cmap='coolwarm')  # Change colormap here (e.g., 'viridis', 'plasma', 'cividis', 'coolwarm')
plt.xlabel("Predicted class")
plt.ylabel("True class")
plt.xticks(np.arange(len(classnames)), classnames)
plt.yticks(np.arange(len(classnames)), classnames)
plt.title("Confusion matrix")
for i in range(len(classnames)):
    for j in range(len(classnames)):
        plt.text(j, i, int(confusion_matrix[i, j]), ha="center", va="center", color="w")
plt.colorbar()
plt.savefig("confusion_matrix.pdf")
plt.show()

#visualize the decision tree
from sklearn.tree import plot_tree
plt.figure()
features_names = ["feature {}".format(i) for i in range(featveclen)]
plot_tree(model, feature_names=features_names, class_names=classnames, filled=True, fontsize=12, proportion=True)
plt.savefig("decision_tree.pdf")
plt.show()

# [5] Evaluate the model robustness
# we choose 30% of the data inside indexes
index_test = np.random.choice(indexes, int(0.3*len(indexes)), replace=False)
index_learn = np.setdiff1d(indexes, index_test)
X_learn, y_learn = index_to_augmentation(index_learn, distorsion_to_add = ["time_shift"])
X_test, y_test = index_to_augmentation(index_test, distorsion_to_add = ["echo"])
X_learn = X_learn/np.linalg.norm(X_learn, axis=1, keepdims=True)
X_test = X_test/np.linalg.norm(X_test, axis=1, keepdims=True)

model = DecisionTreeClassifier(max_depth=best_depth, min_samples_split=best_split)
model.fit(X_learn, y_learn)
predictions = model.predict(X_test)

confusion_matrix = np.zeros((len(classnames), len(classnames)))
for i in range(len(classnames)):
    for j in range(len(classnames)):
        confusion_matrix[i, j] = np.sum((y_test == classnames[i]) & (predictions == classnames[j]))
        
F1_scores = []
for i in range(len(classnames)):
    TP = confusion_matrix[i, i]
    FP = np.sum(confusion_matrix[:, i]) - TP
    FN = np.sum(confusion_matrix[i, :]) - TP
    precision = TP / (TP + FP)
    recall = TP / (TP + FN)
    F1 = 2 * precision * recall / (precision + recall)
    F1_scores.append(F1)
    
mean_F1 = np.mean(F1_scores)
print("F1 score on test set: {}".format(mean_F1))

plt.figure()
plt.imshow(confusion_matrix, cmap='coolwarm')  # Change colormap here (e.g., 'viridis', 'plasma', 'cividis', 'coolwarm')
plt.xlabel("Predicted class")
plt.ylabel("True class")
plt.xticks(np.arange(len(classnames)), classnames)
plt.yticks(np.arange(len(classnames)), classnames)
plt.title("Confusion matrix")
for i in range(len(classnames)):
    for j in range(len(classnames)):
        plt.text(j, i, int(confusion_matrix[i, j]), ha="center", va="center", color="w")
plt.colorbar()
plt.savefig("confusion_matrix_robustness.pdf")
plt.show()
    
 


# [6] Save the trained model
model_dir = "data/models/"
filename = "model.pickle"
model = DecisionTreeClassifier(max_depth=best_depth, min_samples_split=best_split)
model.fit(X, y)
pickle.dump(model, open(model_dir + filename, "wb"))
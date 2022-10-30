"""
================================
Recognizing hand-written digits
================================
This example shows how scikit-learn can be used to recognize images of
hand-written digits, from 0-9.
"""

print(__doc__)

import pickle
import matplotlib.pyplot as plt
import numpy as np
from sklearn import datasets, svm, tree

###############################################################################
# Digits dataset
# --------------
#
# The digits dataset consists of 8x8
# pixel images of digits. The ``images`` attribute of the dataset stores
# 8x8 arrays of grayscale values for each image. We will use these arrays to
# visualize the first 4 images. The ``target`` attribute of the dataset stores
# the digit each image represents and this is included in the title of the 4
# plots below.
#
# Note: if we were working from image files (e.g., 'png' files), we would load
# them using :func:`matplotlib.pyplot.imread`.


###############################################################################
# Classification
# --------------
#
# To apply a classifier on this data, we need to flatten the images, turning
# each 2-D array of grayscale values from shape ``(8, 8)`` into shape
# ``(64,)``. Subsequently, the entire dataset will be of shape
# ``(n_samples, n_features)``, where ``n_samples`` is the number of images and
# ``n_features`` is the total number of pixels in each image.
#
# We can then split the data into train and test subsets and fit a support
# vector classifier on the train samples. The fitted classifier can
# subsequently be used to predict the value of the digit for the samples
# in the test subset.

# import utils.py
import numpy as np
import pickle

# Import datasets, classifiers and performance metrics
from sklearn import datasets, svm, metrics
from sklearn import tree

# Importing rescale, resize, reshape
from skimage.transform import rescale, resize, downscale_local_mean 

from sklearn.model_selection import train_test_split
from sklearn.metrics import precision_score, recall_score, f1_score, accuracy_score


def preprocess(data, scale_factor=1):
    n_samples = len(data)
    data = data.reshape((n_samples, -1))
    print("\ndata:", data.shape)
    if scale_factor == 1:
        return data

    img_rescaled = []
    for img in data:
        img_rescaled.append(rescale(img, scale_factor, anti_aliasing=False))
    img_rescaled = np.array(img_rescaled)
    print("\nimg_rescaled:", img_rescaled.shape)
    return img_rescaled


def data_split(x, y, train_size=0.7, test_size=0.2, val_size=0.1, debug=True):
    # if train_size + test_size + val_size != 1:
    #     print("Invalid ratios: train:test:val split isn't 1!")
    #     return -1
    
    # print("\n from data split:", x.shape, y.shape,train_size, test_size, val_size)
    # split data into train and (test + val) subsets
    x_train, x_test, y_train, y_test = train_test_split(x, y, test_size=(test_size + val_size))

    # split test into test and val
    x_test, x_val, y_test, y_val = train_test_split(x_test, y_test, test_size=val_size/((test_size + val_size)))

    if debug:
        print("\n(x, y) shape:", x.shape, y.shape)
        print("(x_train, y_train) shape:", x_train.shape, y_train.shape)
        print("(x_test, y_test) shape:", x_test.shape, y_test.shape)
        print("(x_val, y_val) shape:", x_val.shape, y_val.shape, end="\n\n")

    return x_train, x_test, x_val, y_train, y_test, y_val


def get_scores(clf, x, y):
    # Predict the value of the digit on the train subset
    predicted = clf.predict(x)
    a = round(accuracy_score(y, predicted), 4)
    p = round(precision_score(y, predicted, average='macro', zero_division=0), 4)
    r = round(recall_score(y, predicted, average='macro', zero_division=0), 4)
    f1 = round(f1_score(y, predicted, average='macro', zero_division=0), 4)

    return [a, p, r, f1]


def digitsClassifier(x, y, gamma=0.001):
    # Create a classifier: a support vector classifier
    clf = svm.SVC(gamma=gamma)
    # Learn the digits on the train subset
    clf.fit(x, y)
    return clf

def decisionClassifier(x, y):
    clf = tree.DecisionTreeClassifier()
    clf.fit(x, y)
    return clf


def save_model(clf, path):
    print("\nSaving the best model...")
    save_file = open(path, 'wb')
    pickle.dump(clf, save_file)
    save_file.close()

def load_model(path):
    print("\nloading the model...")
    load_file = open(path, "rb")
    loaded_model = pickle.load(load_file)
    return 


def train_svm(x_train, y_train, x_val, y_val, x_test, y_test, gammas):
    results_gamma = []
    best_f1 = -1
    gamma_opt = -1
    thres_f1 = 0.11

    for gamma in gammas:
        clf = digitsClassifier(x_train, y_train, gamma)
        
        # predict on train and val sets and get scores
        res_train = get_scores(clf, x_train, y_train)
        res_val = get_scores(clf, x_val, y_val)

        # skippping gammas where accuracy is less than thres_f1
        # validation f1 is 4th elem
        if res_val[3] < thres_f1:
            print(f">> skipping for gamma: {gamma} as {res_val[3]} is less than {thres_f1}")
            continue 
        
        res = [res_train, res_val]
        results_gamma.append(res)

        print(f"\ngamma: {gamma}")
        for s,r in zip(["train", "val"], res):
            print(f"\t{s + ' scores:':<15} {r}")
        print("")

        # validation f1 is 4th elem
        if res_val[3] > best_f1:
            best_f1 = res_val[3]
            gamma_opt = gamma
            best_clf = clf
            best_metrics = res

    # should run only for best gamma 
    res_test = get_scores(best_clf, x_test, y_test)

    print(f"\n\nbest validation f1 score is {best_f1} for optimal gamma {gamma_opt}") 
    print(f"\ttrain scores:     {best_metrics[0]}")
    print(f"\tval scores:       {best_metrics[1]}")
    print(f"\ttest scores:    {res_test}\n\n")

    return gamma_opt


def train_decisionTree(x_train, y_train, x_val, y_val, x_test, y_test, depths):
    results_depth = []
    best_f1 = -1
    depth_opt = -1

    for depth in depths:
        clf = decisionClassifier(x_train, y_train)
        # predict on train and val sets and get scores
        res_train = get_scores(clf, x_train, y_train)
        res_val = get_scores(clf, x_val, y_val)

        res = [res_train, res_val]
        results_depth.append(res)

        print(f"\ndepth: {depth}")
        for s,r in zip(["train", "val"], res):
            print(f"\t{s + ' scores:':<15} {r}")
        print("")


        if res_val[3] > best_f1:
            best_f1 = res_val[3]
            depth_opt = depth
            best_clf = clf
            best_metrics = res

    # should run only for best gamma 
    res_test = get_scores(best_clf, x_test, y_test)

    print(f"\n\nbest validation f1 score is {best_f1} for depth {depth_opt}") 
    print(f"\ttrain scores:     {best_metrics[0]}")
    print(f"\tval scores:       {best_metrics[1]}")
    print(f"\ttest scores:      {res_test}\n\n")

    # print("max_depth:", clf.tree_.max_depth)
    return depth_opt


def train_classifier(x_train, y_train, x_val, y_val, x_test, y_test, clf_type, clf_param):
    if clf_type == 'svm':
        clf = svm.SVC(gamma=clf_param)
    elif clf_type == 'decision':
        clf = tree.DecisionTreeClassifier(max_depth=clf_param)
    else:
        print("Not a valid classifier name.")
        return -1

    clf.fit(x_train, y_train)
    
    # predict on train and val sets and get scores
    res_train = get_scores(clf, x_train, y_train)
    res_val = get_scores(clf, x_val, y_val)
    res_test = get_scores(clf, x_test, y_test)
    
    return [res_train, res_val, res_test]



digits = datasets.load_digits()

print("shape of data:", digits.images.shape)
print("shape of single image:", digits.images[0].shape, end="\n\n")

data_org = digits.images
target = digits.target

data = preprocess(data_org)
x_train, x_test, x_val, y_train, y_test, y_val = data_split(data, target, debug=False)

print("\n***tuning gamma parameter for svm classifier***\n")
gammas =  [0.000005, 0.0001, 0.0005, 0.001, 0.005, 0.01, 0.05, 0.1]
opt_gamma = train_svm(x_train, y_train, x_val, y_val, x_test, y_test, gammas)

print("\n***tuning max_depth parameter for decision tree classifier***\n")
depths = [10, 12, 14, 16, 18, 20] 
opt_depth = train_decisionTree(x_train, y_train, x_val, y_val, x_test, y_test, depths)


# running the classifiers on 5 train:test:val splits for comparison
results_svm = []
results_dt = []

for _ in range(5):
    x_train, x_test, x_val, y_train, y_test, y_val = data_split(data, target, train_size=0.6, test_size=0.3, val_size=0.1, debug=False)

    results_svm.append(train_classifier(x_train, y_train, x_val, y_val, x_test, y_test, clf_type='svm', clf_param=opt_gamma))

    results_dt.append(train_classifier(x_train, y_train, x_val, y_val, x_test, y_test,clf_type='decision', clf_param=opt_depth))


# converting results into numpy array
results_svm_np = np.array([elem[2] for elem in results_svm])
results_dt_np = np.array([elem[2] for elem in results_dt])

print("\n***Printing test scores of both classifiers on 5 train:val:test sets***\n")

for i in range(5):
    print(f"split {i}:     {results_svm_np[i].round(4)}    {results_dt_np[i].round(4)}\n")

# mean and sd
print(f"mean:        {results_svm_np.mean(axis=0).round(4)}     {results_dt_np.mean(axis=0).round(4)}")

print(f"std dev:     {results_svm_np.std(axis=0).round(4)}     {results_dt_np.std(axis=0).round(4)}\n")



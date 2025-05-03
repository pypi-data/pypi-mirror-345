# -*- coding: utf-8 -*-
import time

from transcendent.utils import alloc_shm, load_existing_shm

"""
scores.py
~~~~~~~~~

Functions for producing the various scores used during conformal evaluation,
such as non-conformity measures, credibility and confidence p-values and
probabilities for comparison.

Note that the functions in this module currently only apply to producing
scores for a binary classification task and an SVM classifier. Different
settings and different classifiers will require their own functions for
generating non-conformity measures based on different intuitions.

"""

import logging

import numpy as np
import pandas as pd
from tqdm import tqdm
from multiprocessing import Pool


def get_rf_ncms(clf, X_in, y_in):
    return clf.ncm(X_in, y_in)


def get_svm_ncms(clf, X_in, y_in):
    """Helper functions to get NCMs across an entire pair of X,y arrays."""
    assert hasattr(clf, "decision_function")
    return [
        get_single_svm_ncm(clf, x, y)
        for x, y in tqdm(zip(X_in, y_in), total=len(y_in), desc="svm ncms")
    ]


def get_single_svm_ncm(clf, single_x, single_y):
    """Collect a non-conformity measure from the classifier for `single_x`.

    A note about SVM ncms: In binary classification with a linear SVM, the
    output score is the distance from the hyperplane with respect to the
    positive class. If the score is negative, the prediction is class 0, if
    positive, it's class 1 (in sklearn technically it will be clf.class_[0] and
    clf.class_[1] respectively). To perform thresholding with conformal
    evaluator, we need the distance from the hyperplane with respect to *both*
    classes, so we simply flip the sign to get the 'reflection' for the other
    class.

    Args:
        clf (sklearn.svm.SVC): The classifier to use for the NCMs.
        single_x (np.ndarray): An single feature vector to get the NCM for.
        single_y (int): Either the ground truth (calibration) or predicted
            label (testing) of `single_x`.

    Returns:
        float: The NCM for the given `single_x`.

    """
    assert hasattr(clf, "decision_function")
    decision = clf.decision_function(single_x)

    # If y (ground truth in calibration, prediction in testing) is malware
    # then flip the sign to ensure the most conforming point is most minimal.
    if single_y == 1:
        return -decision
    elif single_y == 0:
        return decision
    raise Exception("Unknown class? Only binary decisions supported.")


def compute_p_values_cred_and_conf(
    clf, train_ncms, groundtruth_train, test_ncms, y_test, X_test
):
    return {
        "conf": compute_confidence_scores(
            clf, train_ncms, groundtruth_train, y_test, X_test
        ),
        "cred": compute_credibility_scores(
            train_ncms, groundtruth_train, test_ncms, y_test
        ),
    }


def creds(args):
    (shm_t, (i, n, m, op_y_labels)) = args
    (train_ncms_t, groundtruth_train_shm_t, ncms_shm_t) = shm_t

    train_ncms_shm, train_ncms = load_existing_shm(*train_ncms_t)
    groundtruth_train_shm, groundtruth_train = load_existing_shm(
        *groundtruth_train_shm_t
    )
    ncms_X_test_op_y_label_shm, ncms_X_test_op_y_label = load_existing_shm(*ncms_shm_t)

    def partial_f(single_ncm_test, single_y_test):
        return compute_single_cred_p_value(
            train_ncms=train_ncms,
            groundtruth_train=groundtruth_train,
            single_y_test=single_y_test,
            single_test_ncm=single_ncm_test,
        )

    res = 1 - max(
        [
            partial_f(single_ncm_test=ncm, single_y_test=op_y)
            for ncm, op_y in zip(
                [ncms_X_test_op_y_label[i + k * m] for k in range(n)], op_y_labels
            )
        ]
    )

    train_ncms_shm.close()
    groundtruth_train_shm.close()
    ncms_X_test_op_y_label_shm.close()
    return res


def compute_credibility_scores(train_ncms, groundtruth_train, test_ncms, y_test):
    return [
        compute_single_cred_p_value(
            train_ncms=train_ncms,
            groundtruth_train=groundtruth_train,
            single_test_ncm=ncm,
            single_y_test=y,
        )
        for ncm, y in tqdm(zip(test_ncms, y_test), total=len(y_test), desc="cred pvals")
    ]


def compute_confidence_scores(clf, train_ncms, groundtruth_train, y_test, X_test):
    unique_y_test_labels = np.unique(y_test)
    y_test_series = pd.Series(y_test, index=X_test.index)

    train_ncms_shm, train_ncms_shm_t = alloc_shm(train_ncms)
    groundtruth_train_shm, groundtruth_train_shm_t = alloc_shm(groundtruth_train)

    conf_X_test = []
    for y in tqdm(
        unique_y_test_labels, total=len(unique_y_test_labels), desc="label conf"
    ):
        op_y_labels = unique_y_test_labels[unique_y_test_labels != y]
        X_test_y = X_test[y_test_series == y]

        m = X_test_y.shape[0]
        n = len(op_y_labels)

        M = pd.concat([X_test_y] * n, ignore_index=True)
        Y = np.concat([np.full(m, op_y_label) for op_y_label in op_y_labels])

        t_start = time.time()
        ncms_X_test_op_y_label = clf.ncm(M, Y)
        ncm_shm, ncm_shm_t = alloc_shm(ncms_X_test_op_y_label)

        shm_t = (train_ncms_shm_t, groundtruth_train_shm_t, ncm_shm_t)
        t_start = time.time()
        with Pool(32) as p:
            conf_X_test_y = p.map(
                creds, [(shm_t, (i, n, m, op_y_labels)) for i in range(m)]
            )

        ncm_shm.close()
        ncm_shm.unlink()

        conf_X_test_y = pd.DataFrame(conf_X_test_y, index=X_test_y.index)
        conf_X_test.append(conf_X_test_y)

    train_ncms_shm.close()
    train_ncms_shm.unlink()
    groundtruth_train_shm.close()
    groundtruth_train_shm.unlink()

    _, conf_X_test = X_test.align(pd.concat(conf_X_test, axis=0), axis=0)
    return conf_X_test


def compute_single_cred_p_value(
    train_ncms, groundtruth_train, single_test_ncm, single_y_test
):
    """Compute a single credibility p-value.

    Credibility p-values describe how 'conformal' a point is with respect to
    the other objects of that class. They're computed as the proportion of
    points with greater NCMs (the number of points _less conforming_ than the
    reference point) over the total number of points.

    Intuitively, a point predicted as malware which is the further away from
    the decision boundary than any other point will have the highest p-value
    out of all other malware points. It will have the smallest NCM (as it is
    the least _non-conforming_) and thus no other points will have a greater
    NCM and it will have a credibility p-value of 1.
    """

    mask = groundtruth_train == single_y_test
    single_cred_p_value = sum((train_ncms >= single_test_ncm) & (mask)) / sum(mask)
    return single_cred_p_value


def get_rf_probs(clf, X_in):
    assert hasattr(clf, "predict_proba")
    logging.info(f"SHAPE RF: {X_in.shape}")
    probability_results = clf.predict_proba(X_in)
    probas_cal_fold = [np.max(t) for t in probability_results]
    pred_proba_cal_fold = [np.argmax(t) for t in probability_results]
    return probas_cal_fold, pred_proba_cal_fold


def get_svm_probs(clf, X_in):
    """Get scores and predictions for comparison with probabilities.

    Note that this function returns the predictions _and_ probabilities given
    by the classifier and that these predictions may different from other
    outputs from the same classifier (such as `predict` or `decision_function`.
    This is due to Platt's scaling (and it's implementation in scikit-learn) in
    which a 5-fold SVM is trained and used to score the observation
    (`predict_proba()` is actually the average of these 5 classifiers).

    The takeaway is to be sure that you're always using probability scores with
    probability predictions and not with the output of other SVC functions.

    Args:
        clf (sklearn.svm.SVC): The classifier to use for the probabilities.
        X_in (np.ndarray): An array of feature vectors to classify.

    Returns:
        (list, list): (Probability scores, probability labels) for `X_in`.

    """
    assert hasattr(clf, "predict_proba")
    probability_results = clf.predict_proba(X_in)
    probas_cal_fold = [np.max(t) for t in probability_results]
    pred_proba_cal_fold = [np.argmax(t) for t in probability_results]
    return probas_cal_fold, pred_proba_cal_fold

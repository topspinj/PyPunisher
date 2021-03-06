#!/usr/bin/env python

"""
Criterion Tests
===============
"""
import os
import sys

import pytest

sys.path.insert(0, os.path.abspath("."))
sys.path.insert(0, os.path.abspath("../"))

import statsmodels.api as sm
from pypunisher.metrics.criterion import aic, bic
from sklearn.linear_model import LinearRegression
from pypunisher.example_data._example_data import X_train, y_train
from tests._wrappers import forward, backward

COMP_TOLERANCE = 500  # comparision tolerance between floats

# -----------------------------------------------------------------------------
# Setup
# -----------------------------------------------------------------------------

sm_model = sm.OLS(y_train, X_train)
res = sm_model.fit()
sm_aic = res.aic
sm_bic = res.bic

# Fit on the contrived test data.
sk_model = LinearRegression().fit(X=X_train, y=y_train)


# -----------------------------------------------------------------------------
# `model` Param
# -----------------------------------------------------------------------------

def test_metric_model_param():
    """Test that the `model` params in `aic()` and `bic()`
    will raise a TypeError when passed something other
    than a sk-learn model."""
    for kind in ("invalid", sk_model):
        for metric in (aic, bic):
            if isinstance(kind, str):
                with pytest.raises(AttributeError):
                    metric(kind, X_train=X_train, y_train=y_train)
            else:
                metric(kind, X_train=X_train, y_train=y_train)


# -----------------------------------------------------------------------------
# Test criterion through selection
# -----------------------------------------------------------------------------

def test_selection_class_use_of_criterion():
    """Test Criterion through `forward()` and `backward()."""

    msg = "`criterion` must be one of: None, 'aic', 'bic'."
    with pytest.raises(ValueError, match=msg):
        forward(min_change=0.5, criterion='acc')

    with pytest.raises(ValueError, match=msg):
        backward(n_features=0.5, criterion='Santa')


# -----------------------------------------------------------------------------
# `data` Param
# -----------------------------------------------------------------------------

def test_metric_data_param():
    """Test that the `data` params in `aic()` and `bic()`
    will raise a TypeError when passed something other
    than an ndarray."""
    for kind in ("invalid", X_train):
        for metric in (aic, bic):
            if isinstance(kind, str):
                with pytest.raises(TypeError):
                    metric(sk_model, X_train=kind, y_train=y_train)
                with pytest.raises(TypeError):
                    metric(sk_model, X_train=X_train, y_train=kind)
            else:
                metric(sk_model, X_train=kind, y_train=y_train)


# -----------------------------------------------------------------------------
# Metric output
# -----------------------------------------------------------------------------


def test_metric_output():
    """Test that both metrics (`aic()` and `bic()`) return
    floating point numbers."""
    for metric in (aic, bic):
        assert isinstance(metric(sk_model, X_train=X_train, y_train=y_train), float)


# -----------------------------------------------------------------------------
# Output Value (Compare against the Stats Models Package).
# -----------------------------------------------------------------------------

def test_metric_output_value():
    """Test that the actual AIC and BIC values computed by
    our functions match that computed by a well-respected
    statistical library in Python (StatsModels)."""
    for metric, comparision in zip((aic, bic), (sm_aic, sm_bic)):
        ours = metric(sk_model, X_train=X_train, y_train=y_train)
        test = ours == pytest.approx(comparision, abs=COMP_TOLERANCE)
        assert test, "`{}()` does not match the value from StatsModels.".format(
            metric.__name__
        )

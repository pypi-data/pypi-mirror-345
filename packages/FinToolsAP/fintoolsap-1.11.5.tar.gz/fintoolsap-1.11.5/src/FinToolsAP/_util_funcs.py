from __future__ import annotations

# standard imports
import os
import numpy
import pandas
import typing
import pathlib
import datetime
import dateutil

# custom imports
import _config

def _rhasattr(obj, attr):
    """
    Recursively checks if an object has an attribute, 
    even if the attribute is nested.

    Parameters:
    obj : object
        The object to check for the attribute.
    attr : str
        The attribute to check, which may be a nested 
        attribute (e.g., 'a.b.c').

    Returns:
    bool
        True if the object has the attribute, False otherwise.
    """
    try:
        # Attempt to split the attribute on the first 
        # dot ('.') to handle nested attributes
        left, right = attr.split('.', 1)
    except:
        # If there is no dot, check if the object has the 
        # simple attribute
        return hasattr(obj, attr)
    # Recursively check the next level of the attribute
    return _rhasattr(getattr(obj, left), right)

def _rgetattr(obj, attr, default = None):
    """
    Recursively retrieves the value of an attribute, even 
    if the attribute is nested.
    Returns a default value if the attribute does not exist.

    Parameters:
    obj : object
        The object to retrieve the attribute from.
    attr : str
        The attribute to retrieve, which may be a nested 
        attribute (e.g., 'a.b.c').
    default : any, optional
        The value to return if the attribute does not exist 
        (default is None).

    Returns:
    any
        The value of the attribute, or the default value if
        the attribute does not exist.
    """
    try:
        # Attempt to split the attribute on the first dot ('.') 
        # to handle nested attributes
        left, right = attr.split('.', 1)
    except:
        # If there is no dot, retrieve the simple attribute or 
        # return the default value
        return getattr(obj, attr, default)
    # Recursively retrieve the next level of the attribute
    return _rgetattr(getattr(obj, left), right, default)

def _rsetattr(obj, attr, val):
    """
    Recursively sets the value of an attribute, even if the
    attribute is nested.

    Parameters:
    obj : object
        The object on which to set the attribute.
    attr : str
        The attribute to set, which may be a nested attribute 
        (e.g., 'a.b.c').
    val : any
        The value to set the attribute to.

    Returns:
    None
    """
    try:
        # Attempt to split the attribute on the first dot ('.')
        # to handle nested attributes
        left, right = attr.split('.', 1)
    except:
        # If there is no dot, set the simple attribute to the 
        # given value
        return setattr(obj, attr, val)
    # Recursively set the next level of the attribute
    return _rsetattr(getattr(obj, left), right, val)


def _check_file_path_type(path, path_arg: str) -> pathlib.Path:
    try:
        path = pathlib.Path(path)
        return(path)
    except:
        raise TypeError(_config.Messages.PATH_FORMAT.format(color = _config.bcolors.FAIL,
                                                            obj = path_arg))

def winsorize(col: pandas.Series, pct_lower: float = None, pct_upper: float = None) -> pandas.Series:
    if(pct_lower is None and pct_upper is None):
        raise ValueError('pct_lower and pct_upper can not bth be None.')
    val_lower, val_upper = -numpy.inf, numpy.inf
    if(pct_lower is not None):
        val_lower = numpy.percentile(col, pct_lower)
    if(pct_upper is not None):
        val_upper = numpy.percentile(col, pct_upper)
    col = numpy.where(col < val_lower, val_lower, col)
    col = numpy.where(col > val_upper, val_upper, col)
    return(col)

def convert_to_list(val: list|str|float|int):
    if(isinstance(val, list)):
        return(val)
    else:
        return([val])

def list_diff(list1: list, list2: list) -> list:
    res = [e for e in list1 if e not in list2]
    return(res)

def list_inter(list1: list, list2: list) -> list:
    res = [e for e in list1 if e in list2]
    return(res)

def msci_quality(Z: float) -> float:
    if(Z >= 0):
        return(1 + Z)
    else:
        return(1 / (1 - Z))
        
        
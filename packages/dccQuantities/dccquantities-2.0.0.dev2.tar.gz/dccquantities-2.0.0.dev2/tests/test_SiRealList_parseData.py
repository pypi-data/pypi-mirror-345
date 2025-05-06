from SiRealList import _parseData as parseData
from metas_unclib import *
import numpy as np
import pytest

from dccXMLJSONConv.dccConv import XMLToDict
from helpers import dccTypeCollector
from dccQuantityParser import parseItemFromJsonDict

from pathlib import Path
import warnings
import os
print("TESTING test_parser.py")
print(os.getcwd())  # Print current working directory

# Define the root directory of the project
ROOT_DIR = Path(__file__).resolve().parent.parent  # Resolve to the root folder

# File-wide variable for the absolute fallback path
ALTERNATIVE_ABS_PATH = Path("/builds/digitaldynamicmeasurement/dccQuantities/")  # Replace with your fallback path
#TODO move this function to tets helpers or so

def get_test_file(*path_parts):
    """
    Tries to fetch the test file, first relative to the current working directory.
    If it doesn't exist, it falls back to the absolute path specified by `ALTERNATIVE_ABS_PATH`.
    """
    # Try relative to the root directory
    test_file = ROOT_DIR / Path(*path_parts)
    if test_file.exists():
        return test_file
    else:
        # If not found, fall back to the absolute path
        test_file = ALTERNATIVE_ABS_PATH / Path(*path_parts)
        if test_file.exists():
            return test_file
        else:
            raise FileNotFoundError(f"Test file not found at {test_file}")


def test_listOfValues():
    data = [1, 2.0, 3.3]
    result = parseData(data)
    assert len(result) == 3
    assert all(result == data)

    data = [ufloat(1, 0.1), ufloat(2, 0.2), ufloat(3, 0.5)]
    result = parseData(data)
    assert len(result) == 3
    assert get_value(result[0]) == 1
    assert get_stdunc(result[1]) == 0.2


def test_listOfTuples():
    data = [(1, 0.1), (2, 0.2), (3.3, 0.5)]
    result = parseData(data)
    assert len(result) == 3
    assert get_value(result[0]) == 1
    assert get_stdunc(result[1]) == 0.2

    with pytest.raises(ValueError):
        data = [(1, 0.1), (2, 0.2), (3.3, 0.5, 4.2)]
        result = parseData(data)


def test_tupleOfLists():
    data = ([1, 2.0, 3], [0.1, 0.2, 0.5])
    result = parseData(data)
    assert len(result) == 3
    assert get_value(result[0]) == 1
    assert get_stdunc(result[1]) == 0.2

    data = (np.array([1, 2.0, 3]), np.array([0.1, 0.2, 0.5]))
    result = parseData(data)
    assert len(result) == 3
    assert get_value(result[0]) == 1
    assert get_stdunc(result[1]) == 0.2

    with pytest.raises(ValueError):
        parseData(([1, 2.0, 3], [0.1, 0.2, 0.5], [4.2, 3.7, 6.9]))
    
    with pytest.raises(ValueError):
        parseData(([1, 2.0, 3], np.array([0.1, 0.2, 0.5])))


def test_dict():
    data = {"values": [1, 2.0, 3], "uncertainties": [0.1, 0.2, 0.5]}
    result = parseData(data)
    assert len(result) == 3
    assert get_value(result[0]) == 1
    assert get_stdunc(result[1]) == 0.2

    data = {"values": np.array([1, 2.0, 3]), "uncertainties": np.array([0.1, 0.2, 0.5])}
    result = parseData(data)
    assert len(result) == 3
    assert get_value(result[0]) == 1
    assert get_stdunc(result[1]) == 0.2

    with pytest.raises(ValueError):
        parseData({"values": [1, 2.0, 3], "uncertainty1": [0.1, 0.2, 0.5], "uncertainty2": [4.2, 3.7, 6.9]})

    with pytest.raises(ValueError):
        parseData({"values": [1, 2.0, 3]})

    with pytest.raises(ValueError):
        parseData({"value": 4.2, "unc": 1.3})

def test_listOfLists():
    data = [[1, 2.0, 3], [0.1, 0.2, 0.5]]
    result = parseData(data)
    assert len(result) == 3
    assert get_value(result[0]) == 1
    assert get_stdunc(result[1]) == 0.2

    data = [np.array([1, 2.0, 3]), np.array([0.1, 0.2, 0.5])]
    result = parseData(data)
    assert len(result) == 3
    assert get_value(result[0]) == 1
    assert get_stdunc(result[1]) == 0.2

    with pytest.raises(ValueError):
        parseData([[1, 0.1], [2.0, 0.2], [3, 0.5]])


def test_321UncerParsing():
    # Use the correct relative paths
    test_file = get_test_file("tests", "data", "simpleSineCalibration.xml")
    with open(test_file, "r") as xml_file:
        xml_data = xml_file.read()
    # parse XML to Json
    jsonDict, errors = XMLToDict(xml_data)

    # get dccQuantities
    quantityDict = dccTypeCollector(jsonDict)

    # parse content to DccQuantityType objects
    dccQuantityTypeObjects = []
    for path, item in quantityDict[-3:]:
        dccQuantityTypeObjects.append(parseItemFromJsonDict(item))
    uncers=dccQuantityTypeObjects[0].uncertainties
    assert len(uncers)==31
    assert uncers[0]==0.00026/2# devide by 2 since we read in expanded Uncer but here we use std_dev
    assert uncers[30]==0.0006/2# devide by 2 since we read in expanded Uncer but here we use std_dev
    pass

def test_reshapingAnd330UncParsing():
    # Use the correct relative paths
    test_file = get_test_file("tests", "data", "sample_flat_table.xml")
    with open(test_file, "r") as xml_file:
        xml_data = xml_file.read()
    # parse XML to Json
    jsonDict, errors = XMLToDict(xml_data)

    # get dccQuantities
    quantityDict = dccTypeCollector(jsonDict)

    # parse content to DccQuantityType objects
    dccQuantityTypeObjects = []
    for path, item in quantityDict[-3:]:
        dccQuantityTypeObjects.append(parseItemFromJsonDict(item))
    testQuantWith10x10data=dccQuantityTypeObjects[2]
    testQuantWith10x10data.reshape(10,10)
    tmp=testQuantWith10x10data[2,9]
    assert tmp.values==3.55
    assert tmp.uncertainties == 0.07938/2# devide by 2 since we read in expanded Uncer but here we use std_dev


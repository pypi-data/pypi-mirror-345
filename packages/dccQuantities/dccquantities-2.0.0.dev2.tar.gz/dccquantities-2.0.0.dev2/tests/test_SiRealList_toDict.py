from SiRealList import SiRealList
import datetime
from metas_unclib import *
import pytest
from helpers import assert_dicts_equal
from collections import OrderedDict
def test_siConstant():
    time = datetime.datetime.now()
    testConstant = SiRealList(
        data=[5],
        label=["test"],
        unit=[r"\one"],
        dateTime=[time],
        _originType="si:constant",
    )

    expectedResult = {
        "si:constant": OrderedDict({"si:label": "test","si:value": 5,  "si:unit": r"\one", "si:dateTime": time})
    }
    assert testConstant.toJsonDict() == expectedResult

    testConstant = SiRealList(
        data=[5],
        unit=[r"\one"],
        _originType="si:constant",
    )

    expectedResult = {
        "si:constant": OrderedDict({"si:value": 5, "si:unit": r"\one"})
    }
    assert testConstant.toJsonDict() == expectedResult

def test_siReal():
    time = datetime.datetime.now()
    testReal = SiRealList(
        data=[4.2],
        label=["asdf"],
        unit=[r"\percent"],
        dateTime=[time],
        _originType="si:real",
    )
    expectedResult = {
        "si:real": OrderedDict({"si:label": "asdf", "si:value": 4.2, "si:unit": r"\percent", "si:dateTime": time})
    }
    assert testReal.toJsonDict() == expectedResult

def test_siRealListXMLList():
    time = datetime.datetime.now()
    testReal = SiRealList(
        data=[4.2, 13.37],
        label=["as", "df"],
        unit=[r"\percent"],
        dateTime=[time],
        _originType="si:realListXMLList",
    )
    expectedResult = {
        "si:realListXMLList": OrderedDict({"si:valueXMLList": np.array([4.2, 13.37]), "si:labelXMLList": ["as", "df"], "si:unitXMLList": [r"\percent"], "si:dateTimeXMLList": [time]}
                                          )}
    assert_dicts_equal(testReal.toJsonDict(),expectedResult)

"""
def test_weirdTypes():
    time = datetime.datetime.now()
    testReal = SiRealList(
        data=[4.2],
        label=["as"],
        unit=[r"\percent"],
        dateTime=[time],
        _originType="si:real",
    )
    testReal.data = np.array([4.2, 13.37])
    testReal.label = ["as", "df"]
    expectedResult = {
        "si:realListXMLList": OrderedDict({"si:valueXMLList": np.array([4.2, 13.37]), "si:labelXMLList": ["as", "df"], "si:unitXMLList": [r"\percent"], "si:dateTimeXMLList": [time]}
                                          )}
    with pytest.warns(UserWarning, match=r'Data list longer than 1, can only serialize to list formats. Will use si:realListXMLList.'):
        assert_dicts_equal(testReal.toJsonDict(),expectedResult)

    with pytest.warns(RuntimeWarning):
        testReal = SiRealList(
            data=np.array([4.2, 13.37]),
            label=["as", "df"],
            unit=[r"\percent"],
            dateTime=[time],
            _originType="si:hypothetical",
        )

    expectedResult = {
        "si:realListXMLList": OrderedDict({"si:valueXMLList": np.array([4.2, 13.37]), "si:labelXMLList": ["as", "df"], "si:unitXMLList": [r"\percent"], "si:dateTimeXMLList": [time]}
                                          )}
    with pytest.warns(UserWarning, match=r'Unknown goal type'):
        assert_dicts_equal(testReal.toJsonDict(),expectedResult)
        pass
"""
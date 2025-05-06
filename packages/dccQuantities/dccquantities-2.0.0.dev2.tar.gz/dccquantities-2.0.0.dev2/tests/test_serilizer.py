from __future__ import annotations  # for type annotation recursion
from typing import Union
# from pathlib import Path
import warnings
import json
import pytest
import os

from dccQuantityParser import parse
print("TESTING test_parser.py")
print(os.getcwd())  # Print current working directory
from testHelpers import get_test_file
from helpers import dccTypeCollector,DCCJSONEncoder
from dccXMLJSONConv.dccConv import XMLToDict, get_from_dict
from json import dumps, loads
def convertToListOfStr(data: Union(object, List[object])) -> List[str]:
    if isinstance(data, list):
        return [str(item) for item in data]
    else:
        return [str(data)]

quantityDataKeysWUnit={'si:real','si:hybrid','si:complex','si:constant','si:realListXMLList','si:complexListXMLList','si:hybridListXMLList','si:constantListXMLList'}
quantityDataKeysWOUnit=['dcc:noQuantity','dcc:charsXMLList']

def test_basic():
    # Use the correct relative paths
    try:
        test_file = get_test_file("tests", "data", "simpleSineCalibration.xml")
        with open(test_file, "r") as xml_file:
            xml_data = xml_file.read()
            # parse XML to Json
            jsonDict, errors = XMLToDict(xml_data)

            # get dccQuantities
            quantityDict = dccTypeCollector(jsonDict)
        dccQunats=parse(xml_data)
    except FileNotFoundError as e:
        warnings.warn(str(e))
    serilizedData=[]
    for q in dccQunats:
        serilizedData.append(q.to_json_dict())
    # check if the first key is 'dcc:qunatity'
    for i,serilized in enumerate(serilizedData):
        try:
            jsonSTR=json.dumps(serilized, cls=DCCJSONEncoder)
        except TypeError as te:
            raise te # to catch unimplemented cases
        simplejsonDict=loads(jsonSTR)
        inputJSONDict=quantityDict[i][1]
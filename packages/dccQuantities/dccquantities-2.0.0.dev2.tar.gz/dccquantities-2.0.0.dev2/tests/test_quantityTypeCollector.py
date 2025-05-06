from helpers import dccTypeCollector
from dccXMLJSONConv.dccConv import XMLToDict, get_from_dict


def test_basic():
    with open("./tests/data/simpleSineCalibration.xml", "r") as xml_file:
        xml_data = xml_file.read()
    testDict,errors = XMLToDict(str(xml_data))
    quantityList = dccTypeCollector(testDict)
    path = quantityList[13][0]
    testContentFromPath = get_from_dict(testDict, path)
    for key, item in quantityList:
        print(item)
    assert len(quantityList) == 15
    assert quantityList[13][1] == testContentFromPath


def test_recursion():
    testDict = {"a": {"a": 1, "b": 2}, "b": {"a": 3, "b": 4}}
    noRecursion = dccTypeCollector(jsonDict=testDict, searchKeys=["a"])
    assert noRecursion == [(["a"], {"a": 1, "b": 2}), (["b", "a"], 3)]
    yesRecursion = dccTypeCollector(
        jsonDict=testDict, searchKeys=["a"], recursive=True
    )
    assert yesRecursion == [(["a"], {"a": 1, "b": 2}), (["a", "a"], 1), (["b", "a"], 3)]
